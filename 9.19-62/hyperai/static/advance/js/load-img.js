//    页码
var pages
var page=function (a) {
    $("#page").paging({
        pageNo:1,    //显示页面
        totalPage: a,   //总页数
        totalSize: 300,
        callback: function(num) {
            pages = num
            console.log('---------',num)

            $.ajax({
                type:'POST',
                url:'/sysmanager/load_local_img',
                data:{'num':num},
                success:function (e) {
                    console.log('-----------',e)

                    $('.mirror-list tr').hide()

                    for (var i = 0;i<e.img_list.length;i++){


                        // $('.clone-box ul').clone().appendTo('.mirror-list')

                        $('.mirror-list tr').eq(i).show()
                        $('.mirror-list tr').eq(i).find('td').eq(0).html(e.img_list[i]['REPOSITORY'])
                        $('.mirror-list tr').eq(i).find('td').eq(1).html(e.img_list[i]['TAG'])
                        $('.mirror-list tr').eq(i).find('td').eq(2).html(e.img_list[i]['SIZE'])
                        $('.mirror-list tr').eq(i).find('td').eq(3).html(e.img_list[i]['IMAGE_ID'])


                        if($('.mirror-list tr').eq(i).find('td').eq(1).html() == '<none></none>'){
                            $('.mirror-list tr').eq(i).find('td').eq(1).html('none')
                            $('.mirror-list tr').eq(i).find('td').eq(3).find('.delete-img').attr('disabled',true)
                            $('.mirror-list tr').eq(i).find('td').eq(3).find('.delete-img').addClass('btn-cl')
                        }
                        if($('.mirror-list tr').eq(i).find('td').eq(0).html() == '<none></none>'){
                            $('.mirror-list tr').eq(i).find('td').eq(0).html('none')
                            $('.mirror-list tr').eq(i).find('td').eq(3).find('.delete-img').attr('disabled',true)
                            $('.mirror-list tr').eq(i).find('td').eq(3).find('.delete-img').addClass('btn-cl')
                        }


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
    url:'/sysmanager/load_local_img',
    success:function (e) {
        console.log('------------',e)
        $('.mirror-list tr').hide()
        for (var i = 0;i<e.img_list.length;i++){


            // $('.clone-box ul').clone().appendTo('.mirror-list')

            $('.mirror-list tr').eq(i).show()
            $('.mirror-list tr').eq(i).find('td').eq(0).html(e.img_list[i]['REPOSITORY'])
            $('.mirror-list tr').eq(i).find('td').eq(1).html(e.img_list[i]['TAG'])
            $('.mirror-list tr').eq(i).find('td').eq(2).html(e.img_list[i]['SIZE'])
            $('.mirror-list tr').eq(i).find('td').eq(3).html(e.img_list[i]['IMAGE_ID'])


            if($('.mirror-list tr').eq(i).find('td').eq(1).html() == '<none></none>'){
                $('.mirror-list tr').eq(i).find('td').eq(1).html('none')
                $('.mirror-list tr').eq(i).find('td').eq(3).find('.delete-img').attr('disabled',true)
                $('.mirror-list tr').eq(i).find('td').eq(3).find('.delete-img').addClass('btn-cl')
            }
            if($('.mirror-list tr').eq(i).find('td').eq(0).html() == '<none></none>'){
                $('.mirror-list tr').eq(i).find('td').eq(0).html('none')
                $('.mirror-list tr').eq(i).find('td').eq(3).find('.delete-img').attr('disabled',true)
                $('.mirror-list tr').eq(i).find('td').eq(3).find('.delete-img').addClass('btn-cl')
            }





        }
        page(e.img_pages)
    }
})









$('.pull-img').on('click',function () {
    $('.create-pj').css('display','block')
})
$('.pj-btn-no').on('click',function (e) {

    $('.create-pj').css('display','none')
    $('.editor-img').hide()
})
$('.pj-div-nav a').on('click',function () {
    $('.create-pj').css('display','none')
    $('.editor-img').hide()
})

$('.tishi-box .alert-btn-yes').click(function () {
    if($(this).parents('.tishi-box').find('.alert-div-content h3').html() == '镜像上传成功！' || $(this).parents('.tishi-box').find('.alert-div-content h3').html() == '正在上传'){
        $.ajax({
            type:'POST',
            url:'/sysmanager/load_local_img',

            success:function (e) {
                console.log('-----------',e)

                $('.mirror-list ul').remove()

                for (var i = 0;i<e.img_list.length;i++){

                    $('.clone-box ul').clone().appendTo('.mirror-list')

                    $('.mirror-list ul').eq(i).find('li').eq(0).html(e.img_list[i]['REPOSITORY'])
                    $('.mirror-list ul').eq(i).find('li').eq(1).html(e.img_list[i]['TAG'])
                    $('.mirror-list ul').eq(i).find('li').eq(2).html(e.img_list[i]['SIZE'])
                    $('.mirror-list ul').eq(i).find('li').eq(3).html(e.img_list[i]['IMAGE_ID'])
                    // if(($('.mirror-list ul').eq(i).find('li').eq(1).html() == '<none></none>' && $('.mirror-list ul').eq(i).find('li').eq(0).html() == '<none></none>') || $('.mirror-list ul').eq(i).find('li').eq(1).html() == '<none></none>' || $('.mirror-list ul').eq(i).find('li').eq(0).html() == '<none></none>'){
                    //     $('.mirror-list ul').eq(i).find('li').eq(3).find('.delete-img').addClass('btn-cl')
                    // }
                    if($('.mirror-list ul').eq(i).find('li').eq(1).html() == '<none></none>'){
                        $('.mirror-list ul').eq(i).find('li').eq(1).html('none')
                        $('.mirror-list ul').eq(i).find('li').eq(3).find('.delete-img').addClass('btn-cl')
                    }
                    if($('.mirror-list ul').eq(i).find('li').eq(0).html() == '<none></none>'){
                        $('.mirror-list ul').eq(i).find('li').eq(0).html('none')
                        $('.mirror-list ul').eq(i).find('li').eq(3).find('.delete-img').addClass('btn-cl')
                    }



                }
            }
        })
    }else if($(this).parents('.tishi-box').find('.alert-div-content h3').html() == '错误'){

    }
    $('.tishi-box').hide()
})



// 上传镜像
$('#pushImg .btn-yes').on('click',function () {
    console.log('*********',$('#project-name').val())
    var reg1 = /.img$/;
    if($('#project-name').val() == ''){
        $('#project-name').parents('.form-group').addClass('has-error')
        $('#project-name').prev('.name_tishi').html('源文件不能为空')
        $('#project-name').prev('.name_tishi').show()
    }else if(!reg1.test($('#project-name').val())){
        $('#project-name').parents('.form-group').addClass('has-error')
        $('#project-name').prev('.name_tishi').html('文件格式不正确')
        $('#project-name').prev('.name_tishi').show()

    }else {
        $.ajax({
            type:"POST",
            url:'/sysmanager/load_add_img',
            data:{'file_name':$('#project-name').val()},
            success:function (e) {
                console.log('**********',e)
                $('.create-pj').css('display','none')
                $('.load-box1').show()
                $('.load-box1 content').html(e.errmsg )


            }
        })
        $('#pushImg').hide()
        $('.modal-backdrop').hide()
    }

})

$('#project-name').focus(function () {
    $(this).parents('.form-group').removeClass('has-error')
    $('.name_tishi').hide()
})






//   编辑
$('.mirror-list').on('click','.editor-img',function () {
    var txt1 = $(this).parents('td').prev('td').prev('td').prev('td').html();
    var txt2 = $(this).parents('td').prev('td').prev('td').prev('td').prev('td').html();
    // var txt3 = $(this).parents('li').siblings('.table-id').html();
    var txt4 = $(this).parents('td').prev('td').html()
    console.log('txt',txt1,txt2,txt4)

    $('#img-name').val(txt2);
    $('#img-tag').val(txt1)
    // $('.tableid').val(txt3)
    $('#imgid').val(txt4)

})

$('#img-name').focus(function () {
    $(this).parents('.form-group').removeClass('has-error')
    $(this).prev('.name_tishi').hide()
})
$('#img-tag').focus(function () {
    $(this).parents('.form-group').removeClass('has-error')
    $(this).prev('.name_tishi').hide()
})



// 编辑
$('#editorImg .btn-yes').on('click',function () {

    $('.img-nameformat').hide()
    var txtname = $('#img-name').val()
    var txttag = $('#img-tag').val()
    console.log('imgname',txtname)
    if (txtname == '') {
        $('#img-name').parents('.form-group').addClass('has-error')
        $('#img-name').prev('.name_tishi').show()
        $('#img-name').prev('.name_tishi').html('镜像名称不能为空')
    } else if (txttag == '') {
        $('#img-tag').parents('.form-group').addClass('has-error')
        $('#img-tag').prev('.name_tishi').show()
        $('#img-tag').prev('.name_tishi').html('标签不能为空')

    }
    else {


        $.ajax({
            type: 'POST',
            url: '/sysmanager/update_tag',
            data: {
                'img_name': txtname,
                'img_tag': txttag,
                'img_id': $('#imgid').val()
            },
            success: function (e) {
                console.log('-----tag----', e)
                // if(e.errmsg == 'success'){
                $('#editorImg').hide()
                $('.modal-backdrop').hide()
                // $('.tishi-box').css('display','block')
                // $('.tishi-box .alert-div-content h3').html(e.errmsg)

                $.ajax({
                    type:'POST',
                    url:'/sysmanager/load_local_img',
                    data:{'num':pages},
                    success:function (e) {
                        console.log('------------',e)
                        $('.mirror-list tr').hide()
                        for (var i = 0;i<e.img_list.length;i++){


                            // $('.clone-box ul').clone().appendTo('.mirror-list')

                            $('.mirror-list tr').eq(i).show()
                            $('.mirror-list tr').eq(i).find('td').eq(0).html(e.img_list[i]['REPOSITORY'])
                            $('.mirror-list tr').eq(i).find('td').eq(1).html(e.img_list[i]['TAG'])
                            $('.mirror-list tr').eq(i).find('td').eq(2).html(e.img_list[i]['SIZE'])
                            $('.mirror-list tr').eq(i).find('td').eq(3).html(e.img_list[i]['IMAGE_ID'])


                            if($('.mirror-list tr').eq(i).find('td').eq(1).html() == '<none></none>'){
                                $('.mirror-list tr').eq(i).find('td').eq(1).html('none')
                                $('.mirror-list tr').eq(i).find('td').eq(3).find('.delete-img').attr('disabled',true)
                                $('.mirror-list tr').eq(i).find('td').eq(3).find('.delete-img').addClass('btn-cl')
                            }
                            if($('.mirror-list tr').eq(i).find('td').eq(0).html() == '<none></none>'){
                                $('.mirror-list tr').eq(i).find('td').eq(0).html('none')
                                $('.mirror-list tr').eq(i).find('td').eq(3).find('.delete-img').attr('disabled',true)
                                $('.mirror-list tr').eq(i).find('td').eq(3).find('.delete-img').addClass('btn-cl')
                            }

                        }
                        page(e.img_pages)
                        $('#page a').each(function () {
                            if($(this).html() == pages){
                                $(this).addClass('current').siblings().removeClass('current')
                            }
                        })
                    }
                })

                // }
            }
        })
    }
})

$('#imgname').on('focus',function () {
    $('.img_tishi').hide()
    $('.img-nameformat').show()
})
$('#img-label').on('focus',function () {
    $('.tag_tishi').hide()
})






// 推送镜像

$('.mirror-list').on('click','.push-img',function () {
    $.ajax({
        type:'POST',
        url:'/sysmanager/push_img',
        data:{'img_name':$(this).parents('td').prev('td').prev('td').prev('td').prev('td').html(),'img_tag':$(this).parents('td').prev('td').prev('td').prev('td').html()},
        success:function (e) {
            console.log('----push---',e)
            if(e.errmsg == '镜像正在push！'){
                // $(this).attr('data-content',e.errmsg)
                // $('.load-box2').show()
                // $('.load-box2 content').html(e.errmsg)

            }else{

                $('.static').show()
                $('#myAlert').addClass('alert-warning').removeClass('alert-success')
                $('.static strong').html(e.errmsg)

            }

        }
    })
})




//删除
var imgs_name,imgs_tag
$('.mirror-list').on('click','.delete-img',function () {
    imgs_name = $(this).parents('td').prev('td').prev('td').prev('td').prev('td').html();
    imgs_tag = $(this).parents('td').prev('td').prev('td').prev('td').html();

    console.log('********name******',imgs_tag,imgs_name)
})
$('#deleteProject .btn-yes').on('click',function () {
    $.ajax({
        type:'POST',
        url:'/sysmanager/delete_node_img',
        data:{'img_name':imgs_name,'img_tag':imgs_tag},
        success:function (e) {
            console.log('------delete-----',e)
            if(e.errmsg == 'success'){
                $('#deleteProject').hide();
                $('.modal-backdrop').hide()

                $.ajax({
                    type:'POST',
                    url:'/sysmanager/load_local_img',
                    data:{'num':pages},
                    success:function (e) {
                        console.log('------------',e)
                        $('.mirror-list tr').hide()
                        for (var i = 0;i<e.img_list.length;i++){


                            // $('.clone-box ul').clone().appendTo('.mirror-list')

                            $('.mirror-list tr').eq(i).show()
                            $('.mirror-list tr').eq(i).find('td').eq(0).html(e.img_list[i]['REPOSITORY'])
                            $('.mirror-list tr').eq(i).find('td').eq(1).html(e.img_list[i]['TAG'])
                            $('.mirror-list tr').eq(i).find('td').eq(2).html(e.img_list[i]['SIZE'])
                            $('.mirror-list tr').eq(i).find('td').eq(3).html(e.img_list[i]['IMAGE_ID'])


                            if($('.mirror-list tr').eq(i).find('td').eq(1).html() == '<none></none>'){
                                $('.mirror-list tr').eq(i).find('td').eq(1).html('none')
                                $('.mirror-list tr').eq(i).find('td').eq(3).find('.delete-img').attr('disabled',true)
                                $('.mirror-list tr').eq(i).find('td').eq(3).find('.delete-img').addClass('btn-cl')
                            }
                            if($('.mirror-list tr').eq(i).find('td').eq(0).html() == '<none></none>'){
                                $('.mirror-list tr').eq(i).find('td').eq(0).html('none')
                                $('.mirror-list tr').eq(i).find('td').eq(3).find('.delete-img').attr('disabled',true)
                                $('.mirror-list tr').eq(i).find('td').eq(3).find('.delete-img').addClass('btn-cl')
                            }

                        }
                        page(e.img_pages)
                        $('#page a').each(function () {
                            if($(this).html() == pages){
                                $(this).addClass('current').siblings().removeClass('current')
                            }
                        })
                    }
                })


            }else{
                $('#deleteProject').hide();
                $('.modal-backdrop').hide();

                $('.static').show()
                $('#myAlert').addClass('alert-warning').removeClass('alert-success')
                $('.static strong').html(e.errmsg)
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


// 查询
$('.btn_select_i').on('click',function () {

    $.ajax({
        type:'POST',
        url:'/sysmanager/load_local_img',
        data:{'name':$('.btn_select_i_text').val()},
        success:function (e) {
            console.log('------------',e)
            $('.mirror-list tr').hide()
            for (var i = 0;i<e.img_list.length;i++){


                // $('.clone-box ul').clone().appendTo('.mirror-list')

                $('.mirror-list tr').eq(i).show()
                $('.mirror-list tr').eq(i).find('td').eq(0).html(e.img_list[i]['REPOSITORY'])
                $('.mirror-list tr').eq(i).find('td').eq(1).html(e.img_list[i]['TAG'])
                $('.mirror-list tr').eq(i).find('td').eq(2).html(e.img_list[i]['SIZE'])
                $('.mirror-list tr').eq(i).find('td').eq(3).html(e.img_list[i]['IMAGE_ID'])


                if($('.mirror-list tr').eq(i).find('td').eq(1).html() == '<none></none>'){
                    $('.mirror-list tr').eq(i).find('td').eq(1).html('none')
                    $('.mirror-list tr').eq(i).find('td').eq(3).find('.delete-img').attr('disabled',true)
                    $('.mirror-list tr').eq(i).find('td').eq(3).find('.delete-img').addClass('btn-cl')
                }
                if($('.mirror-list tr').eq(i).find('td').eq(0).html() == '<none></none>'){
                    $('.mirror-list tr').eq(i).find('td').eq(0).html('none')
                    $('.mirror-list tr').eq(i).find('td').eq(3).find('.delete-img').attr('disabled',true)
                    $('.mirror-list tr').eq(i).find('td').eq(3).find('.delete-img').addClass('btn-cl')
                }





            }
            page(e.img_pages)
        }
    })
})