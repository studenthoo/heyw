$('#opt-fun').on('change',function(){
	if ($(this).val() == 'GD') {
		$('.gd-box').show()
		$('.checkbox-lr').hide()
		$('.gd-box').siblings().hide()
	} else if($(this).val() == 'RMSProp'){
		$('.gd-box').show()
		$('.checkbox-lr').hide()
		$('.gd-box').siblings().hide()
		$('.rmsprop-box').show();
		$('.checkbox-momen').show()
		
	}
	else if($(this).val() == 'Adam'){
		$('.gd-box').show()
		$('.checkbox-lr').show()
		$('.gd-box').siblings().hide()
		$('.adam-box').show();
		
	}
	else if($(this).val() == 'Momentum'){
		$('.gd-box').show()
		$('.checkbox-lr').hide()
		$('.gd-box').siblings().hide()
		$('.rmsprop-momen').show();
		$('.checkbox-momen').hide()
		
	}
})

$('.format-box input').focus(function(){
	$(this).parents('.format-box').find('.format').show()
})
$('.format-box input').blur(function(){
	$(this).parents('.format-box').find('.format').hide()
})



//上传文件
$('#image_list2').on('change',function (e) {
    var file_num = $(this)[0].files.length;
    if(file_num == 1){
        $('.image_list_i_2').val(e.currentTarget.files[0].name)
    }else{
        $('.image_list_i_2').val(file_num + '个文件')
    }
})