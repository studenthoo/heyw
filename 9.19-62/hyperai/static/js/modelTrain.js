$(".user-toggle a").on("click", function() {
                $(".new-model-bac").fadeIn(300);
                $(".new-model").slideDown(350);
        });
$(".new-model-title i").on("click", function() {
                $(".new-model-bac").fadeOut(300);
                $(".new-model").slideUp(350);
        });
$(".cancle-btn").on("click",function(){
				$(".new-model-bac").fadeOut(300);
                $(".new-model").slideUp(350);
})

$(".btn-11").toggle(function(){
	$(this).siblings(".internet").find("select").css("display","none");
	$(this).siblings(".internet").find("input").css("display","inline-block")
},function(){
	$(this).siblings(".internet").find("select").css("display","block");
	$(this).siblings(".internet").find("input").css("display","none")
})
$(".m-inter").focus(function(){
	$(this).css("border","1px solid #00b8b5")
})
$(".m-inter").blur(function(){
	$(this).css("border","1px solid #d9dce1")
})
// A頁面
// $('.btn_yes').on('click',function () {
//     console.log({ 'data_name':$('#model_name').val(),
//         'gaishu':$('#demo_content').val(),
//         'changjing':$('#select_1').val(),
//         'wangluo':$('#select_2').val(),
//         'kuangjia':$('#select_3').val(),
//         'shuju':$('#dataset').val(),
//         'gpu':$('#select_gpus').val()
//     })
//     // 交互
//     $.post('/models/images/classification/new_2',{ 'data_name':$('#model_name').val(),
//         'gaishu':$('#demo_content').val(),
//         'changjing':$('#select_1').val(),
//         'wangluo':$('#select_2').val(),
//         'kuangjia':$('#select_3').val(),
//         'shuju':$('#dataset').val(),
//         'gpu':$('#select_gpus').val()
//     },function (e) {
//         console.log(1)
//     })
// })
// B頁面
// $('.btn_yes2').on('click',function () {
//     console.log({
//         'trainEpoch':$('#train_epochs').val(),
//         'snapshot_interval':$('#snapshot_interval').val(),
//         'val_interval':$('#val_interval').val(),
//         'traces_interval':$('#traces_interval').val(),
//         'random_seed':$('#random_seed').val(),
//         'solver_type':$('#solver_type').val(),
//         'learning_rate':$('#learning_rate').val(),
//         'lr_policy':$('#lr_policy').val(),
//         'lr_step_size':$('#lr_step_size').val(),
//         'lr_step_gamma':$('#lr_step_gamma').val(),
//         'use_mean':$('#use_mean').val(),
//         'crop_size':$('#crop_size').val(),
//         'data__3':$('.data__3').val()
//     })
//     $.post('/models/images/classification/new_3',{
//         'trainEpoch':$('#train_epochs').val(),
//         'snapshot_interval':$('#snapshot_interval').val(),
//         'val_interval':$('#val_interval').val(),
//         'traces_interval':$('#traces_interval').val(),
//         'random_seed':$('#random_seed').val(),
//         'solver_type':$('#solver_type').val(),
//         'learning_rate':$('#learning_rate').val(),
//         'lr_policy':$('#lr_policy').val(),
//         'lr_step_size':$('#lr_step_size').val(),
//         'lr_step_gamma':$('#lr_step_gamma').val(),
//         'use_mean':$('#use_mean').val(),
//         'crop_size':$('#crop_size').val(),
//         'c333':$('.data__3').val()
//     },function (e) {
//         console.log(1)
//     })
// })