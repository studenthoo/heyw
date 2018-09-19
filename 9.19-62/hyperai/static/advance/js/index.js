var round_fun=function(a,b,c,d,f){
			var chart = c3.generate({
				bindto:a,
				title:{text:f},//标题
                tooltip: {
                   show: true,
                    format: {
        //               title: function (d) { return 'Data ' + d; },
                       value: function (value, ratio, id) {
                           var format = id === 'data1' ? d3.format(',') : d3.format('');
                           return format(value);
                       }
                   }
               },
			    data: {
				        columns: b,
//				        [
//				            ['图像', 130],
//				            ['文本', 170],
//				            ['语音', 110],
//				            ['啊啊', 50],
//				            ['啊啊啊', 30]
//				        ],
				        type : 'donut'
				},
		//		汉字显示
				donut: {
					 title: c,
//					 环厚度
					 width:15,
			        label: {
			            format: function (value, ratio, id) {
		//	                 return d3.format('$')(value);
			            }
			        }
			    },
			    legend: {
			        hide: false,
			        position: 'bottom',
//			        图例点击事件
			         item: {
					    onclick: function () {}
					  }
			    },
				color: {
					pattern: d
		        },
                padding:{
                    top:15,
                    bottom:5
                },

		})
	}



var arr3=[
    ['TensorFlow', 1],
    ['Torch', 0],
    ['Caffe', 0]

]
var arr4=[
    ['完成', '1'],
    ['错误', '0'],
    ['运行中', '0']
]

var color3=['#fe6375', '#2674b6', '#03ded6', '#acacac','#e5e6e8']

var color4=['#0dc999', '#bbcdd9', '#ff6276', '#ababab','#e5e6e8']



//    状态
$('.home-state').each(function () {
    if( $(this).html() == 'Waiting'){
        $(this).html('等待')
        $(this).css('background','#ff976a')
    }else if( $(this).html() == 'Running'){
        $(this).html('运行中')
        $(this).css('background','#0dc999')
    }else if( $(this).html() == 'Aborted'){
        $(this).html('终止')
        $(this).css('background','#edeff0')
    }else if( $(this).html() == 'Done'){
        $(this).html('完成')
        $(this).css('background','#ff6376')
    }else if( $(this).html() == 'Error'){
        $(this).html('错误')
        $(this).css('background','#ff976a')
    }

})





<!--checkbox 删除-->
    $('.delete-icon').on('click',function () {
        $('#deleteJob').show()
    })

$('#deleteJob .btn-no').click(function () {
    $('#deleteJob').hide()
})
var job_id = []

$('.delete-icon').on('click',function () {
    job_id = []

    $('.job-box .check_each').each(function () {
        if($(this).is(':checked') == true){
            if($(this).parents('tr').find('.pid').html() == ''){

            }else{
                job_id.push($(this).parents('tr').find('.pid').html())
            }

        }
    })
    console.log(job_id)
})




$('#deleteJob .btn-yes').on('click',function () {
    console.log('----',job_id)
    $.ajax({
        type:'POST',
        url:'/delete_select_job',
        data:{job_all:job_id},
        success:function (e) {
            console.log('delete',e)
            if(e.res == 2){
                $('.delete-box').show()
                $('.delete-box').find('.modal-body').html('数据集已被模型占用、不能删除!')
                $('#deleteJob').hide()

            }else if(e.res == 4){
                console.log(e.err[0])
                if(e.err[0] == 0){


                }else if(e.err[1] == 0){
                    $('.delete-box').show()
                    $('.delete-box').find('.modal-body').html(e.err[0]+'个运行或等待的作业,'+ '请先终止')
                    $('#deleteJob').hide()

                }else{

                    $('.delete-box').show()
                    $('.delete-box').find('.modal-body').html(e.err[0]+'个运行或等待的作业,'+ '请先终止;' + e.err[1]+'个数据集被占用,'+'不能删除')
                    $('#deleteJob').hide()
                }
            }
            else{
                location.reload()
            }
        }
    })


})


//关闭提示框
$(".delete-box .btn-yes").click(function(){
    // $(".alert").alert('close');
    $('.delete-box').hide()

});




