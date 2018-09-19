//	分页点击函数
//   	$("#page").paging({
// 			pageNo:1,    //显示页面
// 			totalPage: 200,   //总页数
// 			totalSize: 300,
// 			callback: function(num) {
// 				console.log({
// 					name:$('.input-info').val(),
// 					pape:num
// 				})
// 			}
// 		})
//	搜索框筛选函数和返回首页
  	$('.btn-3').on('click',function(){
  		console.log($('.input-info').val())
  		$("#page").paging({
			pageNo:1,    //显示页面
			totalPage: 200,   //总页数
			totalSize: 300,
			callback: function(num) {
				console.log({
					name:$('.input-info').val(),
					pape:num
				})
			}
		})
  	})
  	

//新建数据集页面跳转
//href_data_btn href_data
$('.href_data_btn').on('click',function(){
	console.log($('.href_data').html())
	if($('.href_data').html()=='图像分类'){
		window.location.href='/datasets/images/classification/new'
	}
	else if($('.href_data').text()=='其他'){
		window.location.href='/datasets/images/generic/new'
	}
	else if($('.href_data').text()=='图像处理'){
		window.location.href='/datasets/generic/new/image-processing'
	}
	else if($('.href_data').text()=='图像分割'){
		window.location.href='/datasets/generic/new/image-segmentation'
	}
	else if($('.href_data').text()=='目标检测'){
		window.location.href='/datasets/generic/new/image-object-detection'
	}
	else if($('.href_data').text()=='文本分类'){
		window.location.href='/datasets/generic/new/text-classification'
	}
	else if($('.href_data').text()=='医疗影像'){
		window.location.href='/datasets/generic/new/image-sunnybrook'
	}

})
// 删除
// $('.jobb_i').on('click',function () {
// 	// console.log(event.target.id)
// 	console.log($(this).siblings('p').text())
// })
//
// $('.jobb_i').on('click',function () {
// 	console.log($(this).siblings('p').text()+':id')
// 	console.log($(this).siblings('div').text()+':url')
// 	$(this).parent().parent().remove()
// 	$.ajax({
// 		type:'DELETE',
// 		url:$(this).siblings('div').text(),
// 		data:{id:$(this).siblings('p').text()},
// 		success:function (res) {
// 			console.log(res)
// 			if(res.res==2){
// 				alert('该数据集已被模型占用、不能删除!')
// 			}
//         }
// 	})
// })











