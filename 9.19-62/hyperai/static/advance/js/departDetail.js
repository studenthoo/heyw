var department_id = localStorage.getItem('depart_id')
//    页码
var page=function (a) {
    $("#page").paging({
        pageNo:1,    //显示页面
        totalPage: a,   //总页数
        totalSize: 300,
        callback: function(num) {

            console.log('---------',num)

            $.ajax({
                type:'POST',
                url:'/department_load_user',
                data:{'num':num,'depart_id':department_id},
                success:function (e) {
                    console.log('-----------分页',e)

                    $('.user-detail-list tr').hide()
                    for(var i = 0; i < e.user_list.length;i++){
                        $('.user-detail-list tr').eq(i).show()
                        $('.user-detail-list tr').eq(i).children().eq(0).html(e.user_list[i]['name'])
                        $('.user-detail-list tr').eq(i).children().eq(1).html(e.user_list[i]['user_gpu_max'])
                        $('.user-detail-list tr').eq(i).children().eq(2).html(e.user_list[i]['gpu_used'])
                        $('.user-detail-list tr').eq(i).children().eq(4).html(e.user_list[i]['id'])
                    }
                    $('.user-detail-list .gpu_max').each(function () {

                        if($(this).html() == 0){
                            console.log('00000')
                            $(this).parents('tr').find('.d-cluster').attr('disabled',true)
                            $(this).parents('tr').find('.d-cluster').removeClass('btn-green').addClass('btn-gray')
                            $(this).parents('tr').find('.h-cluster').attr('disabled',false)
                            $(this).parents('tr').find('.h-cluster').addClass('btn-green').removeClass('btn-gray')
                        }
                    })
                }
            })

        }
    })
}




<!--加载部门详情信息-->
console.log(localStorage.getItem('depart_id'))

console.log(department_id)
$.ajax({
    type:'POST',
    url:'/department_load_user',
    data:{'depart_id':department_id},
    success:function (e) {
        console.log('加载用户',e)
        $('.depart-gpu').find('span').html(e.gpu_max)
        $('.depart-yxj').html(e.power)
        $('.user-detail-list tr').hide()
        for(var i = 0; i < e.user_list.length;i++){
            $('.user-detail-list tr').eq(i).show()
            $('.user-detail-list tr').eq(i).children().eq(0).html(e.user_list[i]['name'])
            $('.user-detail-list tr').eq(i).children().eq(1).html(e.user_list[i]['user_gpu_max'])
            $('.user-detail-list tr').eq(i).children().eq(2).html(e.user_list[i]['gpu_used'])
            $('.user-detail-list tr').eq(i).children().eq(4).html(e.user_list[i]['id'])
        }

        $('.user-detail-list .gpu_max').each(function () {

            if($(this).html() == 0){
                console.log('00000')
                $(this).parents('tr').find('.d-cluster').attr('disabled',true)
                $(this).parents('tr').find('.d-cluster').removeClass('btn-green').addClass('btn-gray')
                $(this).parents('tr').find('.h-cluster').attr('disabled',false)
                $(this).parents('tr').find('.h-cluster').addClass('btn-green').removeClass('btn-gray')
            }
        })

        page(e.user_page)
    }
})


//	释放资源
var usersid = null
$('.user-detail-list').on('click','.d-cluster',function () {
    usersid = $(this).parents('tr').find('.pid').html()


})



//    释放资源
$('#pauseUse .btn-yes').on('click',function () {


    $.ajax({
        type:'POST',
        url:'/user_release',
        data:{'user_id':usersid},
        success:function (e) {
            console.log('暂停使用',e)
            $('.user-detail-list .pid').each(function () {


                if($(this).html() == e.user_id){

                    $(this).parents('tr').find('td').eq(1).html(e.gpu_max)
                    $(this).parents('tr').find('td').eq(2).html(e.gpu_use)
                    $(this).parents('tr').find('.d-cluster').attr('disabled',true)
                    $(this).parents('tr').find('.d-cluster').removeClass('btn-green').addClass('btn-gray')
                    $(this).parents('tr').find('.h-cluster').attr('disabled',false)
                    $(this).parents('tr').find('.h-cluster').addClass('btn-green').removeClass('btn-gray')
                }
            })

            $('#pauseUse').hide()
            $('.modal-backdrop').hide()
        }
    })



})
//	恢复资源
$('.user-detail-list').on('click','h-cluster',function () {
    usersid = $(this).parents('tr').find('.pid').html()

})
$('#restoreUse .btn-yes').on('click',function () {

    $.ajax({
        type:'POST',
        url:'/user_restore',
        data:{'user_id':usersid},
        success:function (e) {
            console.log('恢复使用',e)
            $('.user-detail-list .pid').each(function () {


                if($(this).html() == e.user_id){

                    $(this).parents('tr').find('td').eq(1).html(e.gpu_max)
                    $(this).parents('tr').find('td').eq(2).html(e.gpu_use)
                    $(this).parents('tr').find('.d-cluster').attr('disabled',false)
                    $(this).parents('tr').find('.d-cluster').removeClass('btn-gray').addClass('btn-green')
                    $(this).parents('tr').find('.h-cluster').attr('disabled',true)
                    $(this).parents('tr').find('.h-cluster').removeClass('btn-green').addClass('btn-gray')

                }
            })
            $('#restoreUse').hide()
            $('.modal-backdrop').hide()
        }
    })

})
