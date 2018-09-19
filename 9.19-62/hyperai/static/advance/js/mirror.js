var pjid = localStorage.getItem('project_id')
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
                url:'/sysmanager/load_img',
                data:{'num':num,'project_id':pjid},
                success:function (e) {
                    console.log('-----------',e)

                    $('.mirror-list tr').hide()

                    for (var i = 0;i<e.img_list.length;i++){

                        var year = new Date(e.img_list[i]['update_time']).getFullYear()
                        var month = new Date(e.img_list[i]['update_time']).getMonth()+1
                        var date = new Date(e.img_list[i]['update_time']).getDate()
                        var hour = new Date(e.img_list[i]['update_time']).getHours();
                        var min = new Date(e.img_list[i]['update_time']).getMinutes();
                        var second = new Date(e.img_list[i]['update_time']).getSeconds();
                        if(month < 10){
                            month = '0' + month
                        }
                        if(date <10){
                            date = '0'+date
                        }
                        if(hour < 10){
                            hour = '0' + hour
                        }
                        if(min < 10){
                            min = '0' + min
                        }
                        if(second < 10){
                            second = '0' + second
                        }

                        $('.mirror-list tr').eq(i).show()
                        // $('.clone-box ul').clone().appendTo('.mirror-list')
                        $('.mirror-list tr').eq(i).find('td').eq(1).html(e.img_list[i]['re_name'])
                        $('.mirror-list tr').eq(i).find('td').eq(2).html(e.img_list[i]['pull_count'])
                        $('.mirror-list tr').eq(i).find('td').eq(3).html(year+'-'+month+'-'+date+' '+hour+':'+min+':'+second)
                        $('.mirror-list tr').eq(i).find('.pid').html(e.img_list[i]['repository_id'])



                    }
                }
            })

        }
    })
}







<!--数据交互-->
console.log(typeof (localStorage.getItem('project_id')))

$.ajax({
    type:'POST',
    url:'/sysmanager/load_img',
    data:{'project_id': pjid},
    success:function (e) {
        console.log('------------',e)
        $('.pj_id').val(localStorage.getItem('project_id'))
        $('.mirror-list tr').hide()
        for (var i = 0;i<e.img_list.length;i++){

            var year = new Date(e.img_list[i]['update_time']).getFullYear()
            var month = new Date(e.img_list[i]['update_time']).getMonth()+1
            var date = new Date(e.img_list[i]['update_time']).getDate()
            var hour = new Date(e.img_list[i]['update_time']).getHours();
            var min = new Date(e.img_list[i]['update_time']).getMinutes();
            var second = new Date(e.img_list[i]['update_time']).getSeconds();
            if(month < 10){
                month = '0' + month
            }
            if(date <10){
                date = '0'+date
            }
            if(hour < 10){
                hour = '0' + hour
            }
            if(min < 10){
                min = '0' + min
            }
            if(second < 10){
                second = '0' + second
            }


            $('.mirror-list tr').eq(i).show()
            // $('.clone-box ul').clone().appendTo('.mirror-list')
            $('.mirror-list tr').eq(i).find('td').eq(1).html(e.img_list[i]['re_name'])
            $('.mirror-list tr').eq(i).find('td').eq(2).html(e.img_list[i]['pull_count'])
            $('.mirror-list tr').eq(i).find('td').eq(3).html(year+'-'+month+'-'+date+' '+hour+':'+min+':'+second)
            $('.mirror-list tr').eq(i).find('.pid').html(e.img_list[i]['repository_id'])



        }
        page(e.img_pages)
    }
})

<!--checkbox 删除-->
var img_id = []





$('.delete-icon').on('click',function () {
    img_id = []

    $('.mirror-list .check_each').each(function () {
        if($(this).is(':checked') == true){
            img_id.push($(this).parents('td').siblings('.pid').html())

        }

    })

    console.log(img_id)
})




$('#deleteProject .btn-yes').on('click',function () {
    console.log('----',img_id)
    $.ajax({
        type:"POST",
        url:"/sysmanager/delete_img",
        data:{"repository_id":img_id},
        success:function (e) {
            console.log('-----',e)
            $('.alert-box').css('display','none')
            if(e.errmsg == 'ok'){
                $('.mirror-list .pid').each(function () {
                    for(var i = 0; i<e.repository_id.length;i++){
                        if($(this).html() == e.repository_id[i]){
                            $(this).parents('tr').remove()
                        }
                    }

                })
                $('.delete-icon').css('visibility','hidden')
                $('#deleteProject').css('display','none')
                $('.modal-backdrop').hide()
            }else{
                $('#deleteProject').css('display','none')
                $('.modal-backdrop').hide()
                $('.static').show()
                $('#myAlert').addClass('alert-warning').removeClass('alert-success')
                $('.static strong').html('删除失败！')
            }

        }
    })


})


//关闭提示框
$(".close").click(function(){
    // $(".alert").alert('close');
    $('.static').css('display','none')
    $('.modal-backdrop').hide()
});



//查询
$('.btn_select_i').on('click',function () {
    $.ajax({
        type:'POST',
        url:'/sysmanager/load_img',
        data:{'name':$('.btn_select_i_text').val(),'project_id':pjid},
        success:function (e) {
            console.log('------search------',e)
            $('.mirror-list tr').hide()

            for (var i = 0;i<e.img_list.length;i++){

                var year = new Date(e.img_list[i]['update_time']).getFullYear()
                var month = new Date(e.img_list[i]['update_time']).getMonth()+1
                var date = new Date(e.img_list[i]['update_time']).getDate()
                var hour = new Date(e.img_list[i]['update_time']).getHours();
                var min = new Date(e.img_list[i]['update_time']).getMinutes();
                var second = new Date(e.img_list[i]['update_time']).getSeconds();
                if(month < 10){
                    month = '0' + month
                }
                if(date <10){
                    date = '0'+date
                }
                if(hour < 10){
                    hour = '0' + hour
                }
                if(min < 10){
                    min = '0' + min
                }
                if(second < 10){
                    second = '0' + second
                }

                $('.mirror-list tr').eq(i).show()
                $('.mirror-list tr').eq(i).find('td').eq(1).html(e.img_list[i]['re_name'])
                $('.mirror-list tr').eq(i).find('td').eq(2).html(e.img_list[i]['pull_count'])
                $('.mirror-list tr').eq(i).find('td').eq(3).html(year+'-'+month+'-'+date+' '+hour+':'+min+':'+second)
                $('.mirror-list tr').eq(i).find('.pid').html(e.img_list[i]['repository_id'])



            }
            page(e.img_pages)
        }
    })
})