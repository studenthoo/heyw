//
// $('#user-name').on('blur',function(){
// 	if(!(/^[a-zA-Z_][0-9a-zA-Z_]{5,15}/.test($(this).val()))){
// 			$('#user-name').val('* 请输入以字母为开头的6-16位账号')
// 			$('#user-name').css('color','red')
// 		}
// 	else{
// 		$.post('/user/name',{'name':$(this).val()},function(e){
// 			if(e.res==1){
// 				$('#user-name').val('* 账号已被注册')
// 			}
// 			else if(e.res==0){
//
// 			}
// 			console.log(e.res)
// 		},'json')
// }
// })
// $('#user-name').on('focus',function(){
// 			$('#user-name').css('color','#999')
// })
$('#user-name').on('blur',function(){
    if(!(/^[a-zA-Z][a-zA-Z0-9_]{5,16}$/.test($(this).val()))){

        $('.user-namenew').show()
        $('#user-name').css('border-bottom','1px solid red')
        console.log('username')
        // $('#user-name').css('color','red')
    }
    else{
        console.log('=========',$(this).val())
        $.post('/user/name',{'name':$(this).val()},function(e){
            if(e.res==1){
                $('.user-nameold').show()
                $('#user-name').css('border-bottom','1px solid red')
            }
            else if(e.res==0){

            }
            console.log(e.res)
        },'json')
    }
})
$('#user-name').on('focus',function(){
    $(this).css('border-bottom','1px solid #00b5b8')
    $('.user-namenew').hide()
    $('.user-nameold').hide()
    $('#user-name').css('color','#999')
})