
////////////////////////////////////////////////表格/
var round_fun=function(a,b,c,d,f){
			var chart = c3.generate({
				bindto:a,
				title:{text:f},//标题
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
					 width:18,
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
		        
		})
	}
	var arr1_txt=JSON.stringify($('.c3_round_ar1').text())
	var arr1_par=JSON.parse(arr1_txt)
	// console.log($('.c3_round_ar1').text())
	console.log(arr1_par)
//表格1
	var arr1=[
			['图像', 130],
			['文本', 170],
			['语音', 110],
			['视频', 50],
			['音频', 30]
		]
	var color1=['#0e9aef', '#fe9868', '#11c888', '#ababab','#e5e6e8']
	round_fun("#mychart-a",arr1,'9',color1,'应用场景')
	$('#mychart-a').children().eq(0).children().eq(3).attr('transform','translate(0,200)')
//表格2
var arr2=[
			['LMDB', 170],
			['HDF5', 70],
			['TFRECORDS', 60]

		]
	var color2=['#10c787', '#ffcc33', '#e5e6e8', '#ababab','#e5e6e8']
	round_fun("#mychart-b",arr2,'10',color2,'数据集');
	$('#mychart-b').children().eq(0).children().eq(3).attr('transform','translate(0,200)')

//表格3
var arr3=[
			['TensorFlow', 160],
			['Torch', 60],
			['Caffe', 90]

		]
	var color3=['#fe6375', '#2674b6', '#03ded6', '#acacac','#e5e6e8']
	round_fun("#mychart-c",arr3,'10',color3,'模型');
	$('#mychart-c').children().eq(0).children().eq(3).attr('transform','translate(0,200)')

////表格3
var arr4=[
			['运行中', 130],
			['完成', 90],
			['停止', 50],
			['未提交', 30]
		]
	var color4=['#0dc999', '#bbcdd9', '#ff6276', '#ababab','#e5e6e8']
	round_fun("#mychart-d",arr4,'10',color4,'作业');
	$('#mychart-d').children().eq(0).children().eq(3).attr('transform','translate(0,200)')

//	
//////////////////////////////////////////////////////////////////////////////////////////页码
// $("#page").paging({
// 			pageNo:1,    //显示页面
// 			totalPage: 200,   //总页数
// 			totalSize: 300,
// 			callback: function(num) {
// 				console.log({
// 					name:$('.c-info').val(),
// 					state_run:$('#c-check-1').prop('checked'),
// 					state_stop:$('#c-check-2').prop('checked'),
// 					state_remove:$('#c-check-3').prop('checked'),
// 					state_done:$('#c-check-4').prop('checked'),
// 					data_begin:$('#datetimepicker3').val(),
// 					data_end:$('#datetimepicker4').val(),
// 					pape:num
// 				})
// 			}
// 		})
$('.bgc-red-h').on('click',function(){
	$(this).parent().parent().slideUp();
	console.log({
		name:$('.c-info').val(),
		state_run:$('#c-check-1').prop('checked'),
		state_stop:$('#c-check-2').prop('checked'),
		state_remove:$('#c-check-3').prop('checked'),
		state_done:$('#c-check-4').prop('checked'),
		data_begin:$('#datetimepicker3').val(),
		data_end:$('#datetimepicker4').val()
		
	});
	// $("#page").paging({
	// 		pageNo:1,    //显示页面
	// 		totalPage: 200,   //总页数
	// 		totalSize: 300,
	// 		callback: function(num) {
	// 			console.log({
	// 				name:$('.c-info').val(),
	// 				state_run:$('#c-check-1').prop('checked'),
	// 				state_stop:$('#c-check-2').prop('checked'),
	// 				state_remove:$('#c-check-3').prop('checked'),
	// 				state_done:$('#c-check-4').prop('checked'),
	// 				data_begin:$('#datetimepicker3').val(),
	// 				data_end:$('#datetimepicker4').val(),
	// 				pape:num
	// 			})
	// 		}
	// 	})
})
//顶部tab选择
//顶部简单三步切换
$('.lis_a_all li').on('click',function(){
	$(this).addClass('bgc-Aqua').siblings().removeClass('bgc-Aqua');
	$(this).removeClass('bgc-gray-a').siblings().addClass('bgc-gray-a');
})
//日历
//$("#datetimepicker_3").on("click",function(){console.log(1)})

	$("#datetimepicker3").on("click",function(e){
		e.stopPropagation();
		console.log(1)
		$(this).lqdatetimepicker({
			css : 'datetime-day',
			dateType : 'D',
			selectback : function(){

			}
		});

	});
	$("#datetimepicker4").on("click",function(e){
		e.stopPropagation();
		$(this).lqdatetimepicker({
			css : 'datetime-day',
			dateType : 'D',
			selectback : function(){

			}
		});

	});
//状态颜色
$('.btn-style').each(function(){
	if($(this).text() == "运行中"){
//		console.log(1)
	$(this).css('backgroundColor','#17d49c')
	}
	else if($(this).text() == "完成"){
		console.log('#ff6376')
		$(this).css('background-color','#ff6376')
	}
	else if($(this).text() == "暂停"){
		$(this).css('background-color','#9eb7c6')
	}
	else if($(this).text() == "错误"){
		$(this).css('background-color','#ff976a')
	}
	else{}
})

// //模型训练背景图
// var bg_all_i=['images/pic/a-1.png',
// 	'images/pic/a-2.png',
// 	'images/pic/a-3.png',
// 	'images/pic/a-4.png',
// 	'images/pic/a-1.png',
// 	'images/pic/a-2.png',
// 	'images/pic/a-3.png',
// 	'images/pic/a-4.png',
// 	'images/pic/a-1.png',
// 	'images/pic/a-2.png'
// ]
//
// $('.pic').each(function(){
// 	$(this).children().attr('src',bg_all_i[Math.floor(Math.random()*10)])
// }
//
//
// )
// 删除模型
// $('.jobb_i').on('click',function () {
// 	console.log($(this).siblings('p').text()+':id')
// 	console.log($(this).siblings('div').text()+':url')
// 	$(this).parent().parent().remove()
// 	$.ajax({
// 		type:'DELETE',
// 		url:$(this).siblings('div').text(),
// 		data:{id:$(this).siblings('p').text()},
// 		success:function (res) {
// 			console.log(res)
// 			if(res.res==2){
// 				alert('该数据集已被模型占用、不能删除!')
// 			}
//         }
// 	})
// })