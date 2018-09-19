// $('.btn-login').on('click',function(){
// 	$.post('/user/login',{
// 		'name':$('#user-name').val(),
// 		'pwd':$('#user-pas').val()
// 	},function(e){
// 		if(e.res==1){
// 			window.location.href='/index'
// 			// alert(e.res)
// 		}
// 		else if(e.res==2){
// 			$('#Tipuser-name').css('display','block')
// 		}
// 		else if(e.res==3){
// 			$('#Tipuser-pas').css('display','block')
// 		}
// 	},'json')
// })
// $('#user-name').on('focus',function(){
// 	$('#Tipuser-name').css('display','none')
// })
// $('#user-pas').on('focus',function(){
// 	$('#Tipuser-pas').css('display','none')
// })
$('.btn-login').on('click',function(){

    if($('#user-name').val() == ''){
        $('#Tipuser-name').css('display','block')
        $('#Tipuser-name').html('* 用户名不能为空')
        return false
    }else if($('#user-pas').val() == ''){
        $('#Tipuser-pas').css('display','block')
        $('#Tipuser-pas').html('* 密码不能为空')
        return false
    }

    $.post('/user/login',{
        'name':$('#user-name').val(),
        'pwd':$('#user-pas').val()
    },function(e){
        if(e.res==1){
            window.location.href='/index'
            // alert(e.res)
        }
        else if(e.res==2){
            $('#Tipuser-name').css('display','block')
            $('#Tipuser-name').html('* 账户不存在')
        }
        else if(e.res==3){
            $('#Tipuser-pas').css('display','block')
            $('#Tipuser-pas').html('* 密码错误')
        }
        else if(e.res==4){
            $('#Tipuser-name').css('display','block')
            $('#Tipuser-name').html('* 账户还没通过审核')
        }
        // else if(e.res==4){
        //     $('#Tipuser-name').css('display','block')
        //     $('#Tipuser-name').html('* 账户还没通过审核')
        // }


    },'json')
})
$('#user-name').on('focus',function(){
    $('#Tipuser-name').css('display','none')
})
$('#user-pas').on('focus',function(){
    $('#Tipuser-pas').css('display','none')
})