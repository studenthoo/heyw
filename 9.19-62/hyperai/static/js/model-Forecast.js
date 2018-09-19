
$('#select_model_cj')[0].selectedIndex = -1;
$('#select_model_cj').on('change',function () {
    if($(this).val()=='classification'){
            $('.last4_snc_ipt').prependTo($('.last4_snc_ipt_box'))
    }
    else {
        $('.last4_snc_ipt').prependTo($('#form_url_all'))
    }
    $('#select_model_model').children().remove();
    $.post('/get_cmodel',{'value':$(this).val()},function (e) {
        var text_all=e.model
        $('#select_model_model')[0].selectedIndex = -1;
        for(var i=0;i<e.model.length;i++){
            console.log(e.model[i][0])
                 $('#select_model_model').append('<option value="'+e.model[i][1]+'">'+e.model[i][0]+'</option>')
            $('#select_model_model')[0].selectedIndex = -1;
            }

    })
    if($(this).val()=='image-sunnybrook' || $(this).val()=='text-classification'){
        console.log('4-4')
        $('.last-forecast-one').css('display','none')
        $('.last-forecast-many').css('display','none')
    }
    else {
        $('.last-forecast-one').css('display','block')
        $('.last-forecast-many').css('display','block')
        $('#custom-inference-form-html').css('display','none')
        $('.text-classifiaction-btn').css('display','none')
    }
    if($(this).val()=='image-sunnybrook'){
       $('.custom-inference-form-i').eq(0).attr('id','custom-inference-form')
        $('.custom-inference-form-html-i').eq(0).attr('id','custom-inference-form-html')
    }
    else if($(this).val()=='text-classification'){
        $('.custom-inference-form-html-i').eq(1).attr('id','custom-inference-form-html')
    }
})
// $('#select_model_model')[0].selectedIndex = -1;
$('#select_model_model').on('change',function () {
            console.log($(this).val())
            $.post('/get_cmodel/detail',{'value':$(this).val()},function (e) {
                console.log(e)
                $('.data_user_nameI').html(' Welcome back,'+e.auth)
                 $('.data_user_name').html(e.auth)
                 $('.data_user_time').html(e.create_time)
                $('.data_user_apply_scence').html(e.apply_scence)
                $('.data_user_framework').html(e.framework)
                $('.data_user_network').html(e.network)
                $('.data_user_database').html(e.database)
                $('.data_user_dataset').html(e.dataset)
                $('.data_user_image_type').html(e.image_type)
                $('.data_user_train_count').html(e.train_count)
                $('.data_user_val_count').html(e.val_count)
                $('.data_user_size').html(e.size)
                $('.data_user_run_time').html(Math.floor(e.run_time)+'秒')
                $('#image_file').on('change',function () {
                    if($('#select_model_cj').val()=='classification'){
                             $('#form_url_all').attr('action','/models/images/classification/classify_one?job_id='+e.job_id)
                    }
                    else {
                         $('#form_url_all').attr('action','/models/images/generic/infer_one?job_id='+e.job_id)
                    }
                     // $('#form_url_all').attr('action','/models/images/classification/classify_one?job_id='+e.job_id)
                })
                $('#image_path').on('click',function () {
                    console.log(1111)
                    if($('#select_model_cj').val()=='classification'){
                        $('#form_url_all').attr('action','/models/images/classification/classify_one?job_id='+e.job_id)
                    }
                    else {
                        $('#form_url_all').attr('action','/models/images/generic/infer_one?job_id='+e.job_id)
                    }
                })
                $('#image_folder').on('click',function () {
                    if($('#select_model_cj').val()=='classification'){
                        $('#form_url_all').attr('action','/models/images/classification/classify_many?job_id='+e.job_id)
                    }
                    else {
                        $('#form_url_all').attr('action','/models/images/generic/infer_many?job_id='+e.job_id)
                    }
                })
                 $('#image_list').on('change',function () {
                     if($('#select_model_cj').val()=='classification'){
                            $('#form_url_all').attr('action','/models/images/classification/classify_many?job_id='+e.job_id)
                    }
                    else {
                        $('#form_url_all').attr('action','/models/images/generic/infer_many?job_id='+e.job_id)
                    }
                     // $('#form_url_all').attr('action','/models/images/classification/classify_many?job_id='+e.job_id)
                })
                 //医疗文本场景
                $('.text-classifiaction-btn').attr('formaction','/models/images/generic/infer_extension?job_id='+e.job_id)
            })
        })