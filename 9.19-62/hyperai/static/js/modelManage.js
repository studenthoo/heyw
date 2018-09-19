
console.log(1)
console.log($('.lis-e-ul .pic').length)
$('.lis-e-ul .pic').on('click',function(){
	window.location.href='dataManage-datasetPreview.html'
})
$('#select_cj')[0].selectedIndex='-1'

$('.btn_new_model').on('click',function () {
   $('.newModel_odiv').css('display','block')
})
$('.btn_new_no').on('click',function () {
   $('.newModel_odiv').css('display','none')
})
var href_all_text=JSON.stringify($('.btn_model_href_all').text())
var href_all=JSON.parse(href_all_text)
	console.log(href_all.Images)
$('.btn_model_href').on('click',function () {
	if ($('#select_cj').val()=='图像分类'){
		window.location.href=$('#Classification').text()
	}
	else if ($('#select_cj').val()=='目标检测'){
		window.location.href=$('.container').children().eq(1).text()
	}
	else if ($('#select_cj').val()=='图像处理'){
		window.location.href=$('.container').children().eq(3).text()
	}
	else if ($('#select_cj').val()=='图像分割'){
		window.location.href=$('.container').children().eq(4).text()
	}
	else if ($('#select_cj').val()=='文本分类'){
		window.location.href=$('.container').children().eq(6).text()
	}
       else if($('#select_cj').val()=='医疗影像'){
               // window.location.href=$('#Sunnybrook').text()
		window.location.href=$('.container').children().eq(5).text()
       }


})
