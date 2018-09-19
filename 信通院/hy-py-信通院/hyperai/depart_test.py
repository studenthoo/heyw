# coding=utf-8
from hyperai.models import Department
from hyperai.ext import db

depart1 = Department(depart_name='部门一',depart_power=1)
depart2 = Department(depart_name='部门二',depart_power=2)
depart3 = Department(depart_name='部门三',depart_power=3)


db.session.add([depart1,depart2,depart3])
db.session.commit()
