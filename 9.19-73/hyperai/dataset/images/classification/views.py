# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import

import os
import shutil

# Find the best implementation available
try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO

import caffe_pb2
import flask
import PIL.Image
import numpy as np
from .forms import ImageClassificationDatasetForm
from .job import ImageClassificationDatasetJob
from hyperai import utils
from PIL import Image
from hyperai.dataset import tasks
from hyperai.utils.forms import fill_form_if_cloned, save_form_to_job
from hyperai.utils.lmdbreader import DbReader
from hyperai.utils.routing import request_wants_json, job_from_request
from hyperai.webapp import scheduler
from hyperai.ext import db
from hyperai.models import Dataset
from datetime import datetime
from hyperai.utils.auth import requires_login

blueprint = flask.Blueprint(__name__, __name__)
def Picture_Fusion(pic_path_1, pic_path_2):
	pic_1 = to_numpy(Image.open(pic_path_1))
	pic_2 = to_numpy(Image.open(pic_path_2))
	fusion = np.append(pic_1, pic_2, axis=1)
	return fusion

def to_numpy(picture):
	return np.array(picture)

def original_meta2new_meta(root, meta_path):
	new_meta_path = meta_path.split('.')[0] + '_new.' + meta_path.split('.')[1]
	new_meta_file = open(new_meta_path, 'w+')

	new_data_path = root + '/new_create_dataset'
	if not os.path.exists(new_data_path):
		os.mkdir(new_data_path)

	original_datas = open(meta_path).readlines()
	update_dates = []
	for index, original_data in enumerate(original_datas):
		split = original_data.split()
		pic_path_1 = root + '/' + split[0]
		pic_path_2 = root + '/' + split[1]
		fusion = Image.fromarray(Picture_Fusion(pic_path_1, pic_path_2))
		fusion_name = pic_path_1.split('_')[1] + '_' +pic_path_2.split('_')[1]
		fusion.save(new_data_path + '/' + fusion_name + '.jpg')
		update_date = fusion_name + '.jpg' + ' '  + split[2] + '\n'
		update_dates.append(update_date)

	for update_date in update_dates:
		new_meta_file.write(update_date)

	new_meta_file.close()

	return new_meta_path, new_data_path

def from_folders(job, form):
	"""
	Add tasks for creating a dataset by parsing folders of images
	"""
	job.labels_file = utils.constants.LABELS_FILE

	# Add ParseFolderTask

	percent_val = form.folder_pct_val.data
	val_parents = []
	if form.has_val_folder.data:
		percent_val = 0

	percent_test = form.folder_pct_test.data
	test_parents = []
	if form.has_test_folder.data:
		percent_test = 0

	min_per_class = form.folder_train_min_per_class.data
	max_per_class = form.folder_train_max_per_class.data

	parse_train_task = tasks.ParseFolderTask(
		job_dir=job.dir(),
		folder=form.folder_train.data,
		percent_val=percent_val,
		percent_test=percent_test,
		min_per_category=min_per_class if min_per_class > 0 else 1,
		max_per_category=max_per_class if max_per_class > 0 else None
	)
	job.tasks.append(parse_train_task)

	# set parents
	if not form.has_val_folder.data:
		val_parents = [parse_train_task]
	if not form.has_test_folder.data:
		test_parents = [parse_train_task]

	if form.has_val_folder.data:
		min_per_class = form.folder_val_min_per_class.data
		max_per_class = form.folder_val_max_per_class.data

		parse_val_task = tasks.ParseFolderTask(
			job_dir=job.dir(),
			parents=parse_train_task,
			folder=form.folder_val.data,
			percent_val=100,
			percent_test=0,
			min_per_category=min_per_class if min_per_class > 0 else 1,
			max_per_category=max_per_class if max_per_class > 0 else None
		)
		job.tasks.append(parse_val_task)
		val_parents = [parse_val_task]

	if form.has_test_folder.data:
		min_per_class = form.folder_test_min_per_class.data
		max_per_class = form.folder_test_max_per_class.data

		parse_test_task = tasks.ParseFolderTask(
			job_dir=job.dir(),
			parents=parse_train_task,
			folder=form.folder_test.data,
			percent_val=0,
			percent_test=100,
			min_per_category=min_per_class if min_per_class > 0 else 1,
			max_per_category=max_per_class if max_per_class > 0 else None
		)
		job.tasks.append(parse_test_task)
		test_parents = [parse_test_task]

	# Add CreateDbTasks

	backend = form.backend.data
	encoding = form.encoding.data
	compression = form.compression.data

	job.tasks.append(
		tasks.CreateDbTask(
			job_dir=job.dir(),
			parents=parse_train_task,
			input_file=utils.constants.TRAIN_FILE,
			db_name=utils.constants.TRAIN_DB,
			backend=backend,
			image_dims=job.image_dims,
			resize_mode=job.resize_mode,
			encoding=encoding,
			compression=compression,
			mean_file=utils.constants.MEAN_FILE_CAFFE,
			labels_file=job.labels_file,
		)
	)

	if percent_val > 0 or form.has_val_folder.data:
		job.tasks.append(
			tasks.CreateDbTask(
				job_dir=job.dir(),
				parents=val_parents,
				input_file=utils.constants.VAL_FILE,
				db_name=utils.constants.VAL_DB,
				backend=backend,
				image_dims=job.image_dims,
				resize_mode=job.resize_mode,
				encoding=encoding,
				compression=compression,
				labels_file=job.labels_file,
			)
		)

	if percent_test > 0 or form.has_test_folder.data:
		job.tasks.append(
			tasks.CreateDbTask(
				job_dir=job.dir(),
				parents=test_parents,
				input_file=utils.constants.TEST_FILE,
				db_name=utils.constants.TEST_DB,
				backend=backend,
				image_dims=job.image_dims,
				resize_mode=job.resize_mode,
				encoding=encoding,
				compression=compression,
				labels_file=job.labels_file,
			)
		)


def from_files(job, form):
	"""
	Add tasks for creating a dataset by reading textfiles
	"""
	# labels
	pic_num = form.pic_num.data
	# print pic_num
	if form.textfile_use_local_files.data:
		labels_file_from = form.textfile_local_labels_file.data.strip()
		labels_file_to = os.path.join(job.dir(), utils.constants.LABELS_FILE)
		shutil.copyfile(labels_file_from, labels_file_to)
	else:
		flask.request.files[form.textfile_labels_file.name].save(
			os.path.join(job.dir(), utils.constants.LABELS_FILE)
		)
	job.labels_file = utils.constants.LABELS_FILE

	shuffle = bool(form.textfile_shuffle.data)
	backend = form.backend.data
	encoding = form.encoding.data
	compression = form.compression.data


	image_folder = form.textfile_train_folder.data.strip()
	if not image_folder:
		image_folder = None
	# train
	if form.textfile_use_local_files.data:
		if pic_num == 1:
			train_file = form.textfile_local_train_images.data.strip()
		elif pic_num == 2:
			train_file_txt = form.textfile_local_train_images.data.strip()
			train_file,image_folder = original_meta2new_meta(image_folder,train_file_txt)

	else:
		flask.request.files[form.textfile_train_images.name].save(
			os.path.join(job.dir(), utils.constants.TRAIN_FILE)
		)

		if pic_num == 1:
			train_file = utils.constants.TRAIN_FILE
		elif pic_num == 2:
			train_file_txt = utils.constants.TRAIN_FILE
			train_file,image_folder = original_meta2new_meta(image_folder,train_file_txt)


	job.tasks.append(
		tasks.CreateDbTask(
			job_dir=job.dir(),
			input_file=train_file,
			db_name=utils.constants.TRAIN_DB,
			backend=backend,
			image_dims=job.image_dims,
			image_folder=image_folder,
			resize_mode=job.resize_mode,
			encoding=encoding,
			compression=compression,
			mean_file=utils.constants.MEAN_FILE_CAFFE,
			labels_file=job.labels_file,
			shuffle=shuffle,
		)
	)

	# val

	image_folder = form.textfile_val_folder.data.strip()
	if not image_folder:
		image_folder = None
	if form.textfile_use_val.data:
		if form.textfile_use_local_files.data:
			if pic_num == 1:
				val_file = form.textfile_local_val_images.data.strip()
			elif pic_num == 2:
				val_file_txt = form.textfile_local_val_images.data.strip()
				val_file, image_folder = original_meta2new_meta(image_folder, val_file_txt)
		else:
			flask.request.files[form.textfile_val_images.name].save(
				os.path.join(job.dir(), utils.constants.VAL_FILE)
			)
			if pic_num == 1:
				val_file = utils.constants.VAL_FILE
			elif pic_num == 2:
				val_file_txt = utils.constants.VAL_FILE
				val_file, image_folder = original_meta2new_meta(image_folder, val_file_txt)



		job.tasks.append(
			tasks.CreateDbTask(
				job_dir=job.dir(),
				input_file=val_file,
				db_name=utils.constants.VAL_DB,
				backend=backend,
				image_dims=job.image_dims,
				image_folder=image_folder,
				resize_mode=job.resize_mode,
				encoding=encoding,
				compression=compression,
				labels_file=job.labels_file,
				shuffle=shuffle,
			)
		)

	# test


	image_folder = form.textfile_test_folder.data.strip()
	if not image_folder:
		image_folder = None
	if form.textfile_use_test.data:
		if form.textfile_use_local_files.data:
			if pic_num == 1:
				test_file = form.textfile_local_test_images.data.strip()
			elif pic_num == 2:
				test_file_txt = form.textfile_local_test_images.data.strip()
				test_file, image_folder = original_meta2new_meta(image_folder, test_file_txt)
		else:
			flask.request.files[form.textfile_test_images.name].save(
				os.path.join(job.dir(), utils.constants.TEST_FILE)
			)
			if pic_num == 1:
				test_file = utils.constants.TEST_FILE
			elif pic_num == 2:
				test_file_txt = utils.constants.TEST_FILE
				test_file, image_folder = original_meta2new_meta(image_folder, test_file_txt)



		job.tasks.append(
			tasks.CreateDbTask(
				job_dir=job.dir(),
				input_file=test_file,
				db_name=utils.constants.TEST_DB,
				backend=backend,
				image_dims=job.image_dims,
				image_folder=image_folder,
				resize_mode=job.resize_mode,
				encoding=encoding,
				compression=compression,
				labels_file=job.labels_file,
				shuffle=shuffle,
			)
		)

def from_s3(job, form):
	"""
	Add tasks for creating a dataset by parsing s3s of images
	"""
	job.labels_file = utils.constants.LABELS_FILE

	# Add Parses3Task

	percent_val = form.s3_pct_val.data
	val_parents = []

	percent_test = form.s3_pct_test.data
	test_parents = []

	min_per_class = form.s3_train_min_per_class.data
	max_per_class = form.s3_train_max_per_class.data

	delete_files = not form.s3_keepcopiesondisk.data

	parse_train_task = tasks.ParseS3Task(
		job_dir=job.dir(),
		s3_endpoint_url=form.s3_endpoint_url.data,
		s3_bucket=form.s3_bucket.data,
		s3_path=form.s3_path.data,
		s3_accesskey=form.s3_accesskey.data,
		s3_secretkey=form.s3_secretkey.data,
		percent_val=percent_val,
		percent_test=percent_test,
		min_per_category=min_per_class if min_per_class > 0 else 1,
		max_per_category=max_per_class if max_per_class > 0 else None
	)
	job.tasks.append(parse_train_task)

	# set parents
	val_parents = [parse_train_task]
	test_parents = [parse_train_task]

	# Add CreateDbTasks

	backend = form.backend.data
	encoding = form.encoding.data
	compression = form.compression.data

	job.tasks.append(
		tasks.CreateDbTask(
			job_dir=job.dir(),
			parents=parse_train_task,
			input_file=utils.constants.TRAIN_FILE,
			db_name=utils.constants.TRAIN_DB,
			backend=backend,
			image_dims=job.image_dims,
			resize_mode=job.resize_mode,
			encoding=encoding,
			compression=compression,
			mean_file=utils.constants.MEAN_FILE_CAFFE,
			labels_file=job.labels_file,
			delete_files=delete_files,
		)
	)

	if percent_val > 0:
		job.tasks.append(
			tasks.CreateDbTask(
				job_dir=job.dir(),
				parents=val_parents,
				input_file=utils.constants.VAL_FILE,
				db_name=utils.constants.VAL_DB,
				backend=backend,
				image_dims=job.image_dims,
				resize_mode=job.resize_mode,
				encoding=encoding,
				compression=compression,
				labels_file=job.labels_file,
				delete_files=delete_files,
			)
		)

	if percent_test > 0:
		job.tasks.append(
			tasks.CreateDbTask(
				job_dir=job.dir(),
				parents=test_parents,
				input_file=utils.constants.TEST_FILE,
				db_name=utils.constants.TEST_DB,
				backend=backend,
				image_dims=job.image_dims,
				resize_mode=job.resize_mode,
				encoding=encoding,
				compression=compression,
				labels_file=job.labels_file,
				delete_files=delete_files,
			)
		)


@blueprint.route('/new', methods=['GET'])
@requires_login
def new():
	"""
	Returns a form for a new ImageClassificationDatasetJob
	"""
	form = ImageClassificationDatasetForm()

	# Is there a request to clone a job with ?clone=<job_id>
	fill_form_if_cloned(form)
	if form.method.data == 'folder':
		mark = 'mark'
	elif form.method.data == 'textfile':
		mark = 'no_mark'
	return flask.render_template('datasets/images/classification/new2.html', form=form, mark=mark)


# @blueprint.route('.json', methods=['POST'])
@blueprint.route('', methods=['POST'], strict_slashes=False)
@requires_login
def create():
	"""
	Creates a new ImageClassificationDatasetJob

	Returns JSON when requested: {job_id,name,status} or {errors:[]}
	"""
	form = ImageClassificationDatasetForm()
 
	# Is there a request to clone a job with ?clone=<job_id>
	fill_form_if_cloned(form)

	if not form.validate_on_submit():
		if request_wants_json():
			return flask.jsonify({'errors': form.errors}), 400
		else:
			return flask.render_template('datasets/images/classification/new2.html', form=form), 400

	job = None
	if form.method.data == 'folder':
		name = form.dataset_name.data
		desc = form.dataset_desc.data
	elif form.method.data == 'textfile':
		name = form.dataset_name_text.data
		desc = form.dataset_desc_text.data
	try:
		job = ImageClassificationDatasetJob(
			username=utils.auth.get_username(),
			name=name,
			group=form.group_name.data,
			image_dims=(
				int(form.resize_height.data),
				int(form.resize_width.data),
				int(form.resize_channels.data),
			),
			resize_mode=form.resize_mode.data,
			desc=desc,
		)

		if form.method.data == 'folder':
			from_folders(job, form)

		elif form.method.data == 'textfile':
			from_files(job, form)

		elif form.method.data == 's3':
			from_s3(job, form)

		else:
			raise ValueError('method not supported')

		# Save form data with the job so we can easily clone it later.
		save_form_to_job(job, form)

		scheduler.add_job(job)
		if request_wants_json():

			return flask.jsonify(job.json_dict())
		else:

			return flask.redirect(flask.url_for('hyperai.dataset.views.show', job_id=job.id()))

	except:
		if job:
			scheduler.delete_job(job)
		raise

@requires_login
def show(job, related_jobs=None):
	"""
	Called from hyperai.dataset.views.datasets_show()
	"""
	# user = flask.request.cookies['username']
	return flask.render_template('datasets/images/classification/show1.html', job=job, related_jobs=related_jobs)


def summary(job):
	"""
	Return a short HTML summary of an ImageClassificationDatasetJob
	"""
	return flask.render_template('datasets/images/classification/summary.html',
								 dataset=job)


@blueprint.route('/explore', methods=['GET'])
@requires_login
def explore():
	"""
	Returns a gallery consisting of the images of one of the dbs
	"""
	job = job_from_request()
	# Get LMDB
	db = flask.request.args.get('db', 'train')
	if 'train' in db.lower():
		task = job.train_db_task()
	elif 'val' in db.lower():
		task = job.val_db_task()
	elif 'test' in db.lower():
		task = job.test_db_task()
	if task is None:
		raise ValueError('No create_db task for {0}'.format(db))
	if task.status != 'D':
		raise ValueError("This create_db task's status should be 'D' but is '{0}'".format(task.status))
	if task.backend != 'lmdb':
		raise ValueError("Backend is {0} while expected backend is lmdb".format(task.backend))
	db_path = job.path(task.db_name)
	labels = task.get_labels()

	page = int(flask.request.args.get('page', 0))
	size = int(flask.request.args.get('size', 25))
	label = flask.request.args.get('label', None)

	if label is not None:
		try:
			label = int(label)
		except ValueError:
			label = None

	reader = DbReader(db_path)
	count = 0
	imgs = []

	min_page = max(0, page - 5)
	if label is None:
		total_entries = reader.total_entries
	else:
		total_entries = task.distribution[str(label)]['count']

	max_page = min((total_entries - 1) / size, page + 5)
	pages = range(min_page, max_page + 1)
	for key, value in reader.entries():
		if count >= page * size:
			datum = caffe_pb2.Datum()
			datum.ParseFromString(value)
			if label is None or datum.label == label:
				if datum.encoded:
					s = StringIO()
					s.write(datum.data)
					s.seek(0)
					img = PIL.Image.open(s)
				else:
					import caffe.io
					arr = caffe.io.datum_to_array(datum)
					# CHW -> HWC
					arr = arr.transpose((1, 2, 0))
					if arr.shape[2] == 1:
						# HWC -> HW
						arr = arr[:, :, 0]
					elif arr.shape[2] == 3:
						# BGR -> RGB
						# XXX see issue #59
						arr = arr[:, :, [2, 1, 0]]
					img = PIL.Image.fromarray(arr)
				imgs.append({"label": labels[datum.label], "b64": utils.image.embed_image_html(img)})
		if label is None:
			count += 1
		else:
			datum = caffe_pb2.Datum()
			datum.ParseFromString(value)
			if datum.label == int(label):
				count += 1
		if len(imgs) >= size:
			break

	return flask.render_template(
		'datasets/images/explore.html',
		page=page, size=size, job=job, imgs=imgs, labels=labels,
		pages=pages, label=label, total_entries=total_entries, db=db)
