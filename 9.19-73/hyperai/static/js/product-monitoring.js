//if(msg['update'] == 'gpu_utilization'){
////                GPU CPU
//              console.log(msg['data'])
//              console.log(msg)
//              console.log(msg['data']['data_gpu'].length)
//              $('.resource-content').children().remove()
//
//              var resource_parent=msg['data']['data_gpu'].length
//              for(var i=0;i<resource_parent;i++){
//                  $('.resource-all .resource-parent').clone().appendTo($('.resource-content'))
//              }
//              for(var i=0;i<resource_parent;i++){
//                  for(var j=0;j<msg['data']['data_gpu'][i]['value'].length;j++){
//                      $('.resource-all .resource-children').clone().appendTo($('.resource-content').children().eq(i))
//                      $('.resource-content').children().css('display','block')
//                      $('.resource-content').children().children().css('display','block')
//                      $('.resource-content .resource-parent').eq(i).children('.resource-children').eq(j).children().eq(2).children().children().children().children().children().children().css('width',msg['data']['data_gpu'][i]['value'][j]['utilization']['gpu'])
//                      $('.resource-content .resource-parent').eq(i).children('.resource-children').eq(j).children().eq(2).children().children().children().children().children().children().html(msg['data']['data_gpu'][i]['value'][j]['utilization']['gpu'])
//                      $('.resource-content .resource-parent').eq(i).children('.resource-children').eq(j).children().eq(4).children().children().children().children().children().children().css('width',(Math.floor(msg['data']['data_gpu'][i]['value'][j]['memory']['used']/msg['data']['data_gpu'][i]['value'][j]['memory']['total']*100)+'%'))
//                      $('.resource-content .resource-parent').eq(i).children('.resource-children').eq(j).children().eq(4).children().children().children().children().children().children().html((Math.floor(msg['data']['data_gpu'][i]['value'][j]['memory']['used']/msg['data']['data_gpu'][i]['value'][j]['memory']['total']*100)+'%'))
//                      $('.resource-content .resource-parent').eq(i).children('.resource-children').eq(j).children().eq(6).children().children().children().children().children().children().css('width','100%')
//                      $('.resource-content .resource-parent').eq(i).children('.resource-children').eq(j).children().eq(6).children().children().children().children().children().children().html(msg['data']['data_gpu'][i]['value'][j]['temperature']+'℃')
//
//
//                  }
//              }
//              for(var i=0;i<resource_parent;i++){
//                  $('.resource-content .resource-parent').eq(i).children().first().children().children().children().html('容器'+(i+1))
//                  for(var j=0;j<msg['data']['data_gpu'][i]['value'].length;j++){
//                      $('.resource-content .resource-parent').eq(i).children('.resource-children').eq(j).children().eq(0).children().children().children().html('卡'+(j+1))
//
//                  }
//              }
//          }

//监控曲线
function c3_aa(a){
        c3.generate($.extend({
            bindto: '#chart-monitoring',
//          title:{text:'zuoye',},//标题
            axis: {
                x: {
                    tick: {
                        // 3 sig-digs
                        format: function(x) { return Math.round(x * 1000) / 1000; },
                      fit: false,   //坐标位点偏移量
//						count:7
//						culling: {
//						                    max: 7 //刻度显示数量
//						                }
                    },
                    min: 0,
                    padding: {left: 0},
                     label: {
                        text: '[时间/小时]',
                        position: 'outer-right',
                    },
                },
                y: {
                    min: 0,
//                  max:90,
                    padding: {bottom: 0},
                },
                y2: {
                    show: true,
//                 		 最值
                    min: 0,
                    max: 10,
                    padding: {top: 0, bottom: 0},
                },
            },
            color: {
       			 pattern: ['#0e9aef', 'red', '#11c888', '#ababab','#e5e6e8']

       		},
       		point: {
//     			参数点半径
			      r: 2,
			},
            grid: {x: {show: true},
//            	y: {show: true}
            },
            legend: {position: 'bottom'},
        },
        {
             data: a,
//            data: {
//		    	axes: {
////		    		给data3额外添加Y轴
//			        "accuracy-val": 'y2' // ADD
//			     },
//		        columns: a
//		    },
            transition: {
                duration: 0,
            },
            subchart: {
                show: true,
            },
            zoom: {
                rescale: true,
            },
        }
        ));
        }
 c3_aa({'xs': {'accuracy-val': 'val_epochs', 'loss-train': 'train_epochs'},
	 'axes': {'accuracy-val': 'y2'}, 
	 'names': {'accuracy-val': '失败次数', 'loss-train': '成功次数'}, 
	 'columns': [
//	 0, 35, 75, 55, 65, 25, 35, 70, 68, 55, 66
			 ['loss-train', 0, 35, 75, 55, 65, 25, 35, 70, 68, 55, 66],
			 ['train_epochs', 0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
			 ['accuracy-val',0, 1.0,1, 0, 0, 0, 1.0, 0, 0, 1, 0],
			 ['val_epochs', 0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
		 ]
	 })



var GPU=['80%','90%']
var GB=['77%','89%']
var CC=['52℃','60℃']
var GPU_i=1


function aj_content() {
    $('.resource-content').children().remove()
    for(var i=0;i<1;i++){
        $('.resource-all .resource-parent').clone().appendTo($('.resource-content'))
    }
    for(var i=0;i<1;i++){
        for(var j=0;j<2;j++){
            $('.resource-all .resource-children').clone().appendTo($('.resource-content').children().eq(i))
            $('.resource-content').children().css('display','block')
            $('.resource-content').children().children().css('display','block')
            $('.resource-content .resource-parent').eq(i).children('.resource-children').eq(j).children().eq(2).children().children().children().children().children().children().css('width',GPU[j])
            $('.resource-content .resource-parent').eq(i).children('.resource-children').eq(j).children().eq(2).children().children().children().children().children().children().html(GPU[j])
            $('.resource-content .resource-parent').eq(i).children('.resource-children').eq(j).children().eq(4).children().children().children().children().children().children().css('width',GB[j])
            $('.resource-content .resource-parent').eq(i).children('.resource-children').eq(j).children().eq(4).children().children().children().children().children().children().html(GB[j])
            $('.resource-content .resource-parent').eq(i).children('.resource-children').eq(j).children().eq(6).children().children().children().children().children().children().css('width','100%')
            $('.resource-content .resource-parent').eq(i).children('.resource-children').eq(j).children().eq(6).children().children().children().children().children().children().html(CC[j])

        }
    }
}
setInterval(function () {
    GPU_i++
    if(GPU_i % 2 ==0){
         GPU=['89%','75%']
         GB=['79%','92%']
         CC=['65℃','70℃']
        aj_content()
    }
    else if(GPU_i % 3 ==0){
         GPU=['65%','80%']
         GB=['82%','85%']
         CC=['56℃','67℃']
        aj_content()
    }
    else if(GPU_i % 5 ==0){
        GPU=['68%','84%']
        GB=['88%','83%']
        CC=['59℃','77℃']
        aj_content()
    }
    else {
        GPU=['61%','94%']
        GB=['80%','93%']
        CC=['69℃','87℃']
        aj_content()
    }

    // console.log(GPU_i % 2)
},2000)
// for(var i=0;i<1;i++){
//     for(var j=0;j<2;j++){
//         $('.resource-all .resource-children').clone().appendTo($('.resource-content').children().eq(i))
//         $('.resource-content').children().css('display','block')
//         $('.resource-content').children().children().css('display','block')
//         $('.resource-content .resource-parent').eq(i).children('.resource-children').eq(j).children().eq(2).children().children().children().children().children().children().css('width',GPU[j])
//         $('.resource-content .resource-parent').eq(i).children('.resource-children').eq(j).children().eq(2).children().children().children().children().children().children().html(GPU[j])
//         $('.resource-content .resource-parent').eq(i).children('.resource-children').eq(j).children().eq(4).children().children().children().children().children().children().css('width',GB[j])
//         $('.resource-content .resource-parent').eq(i).children('.resource-children').eq(j).children().eq(4).children().children().children().children().children().children().html(GB[j])
//         $('.resource-content .resource-parent').eq(i).children('.resource-children').eq(j).children().eq(6).children().children().children().children().children().children().css('width','100%')
//         $('.resource-content .resource-parent').eq(i).children('.resource-children').eq(j).children().eq(6).children().children().children().children().children().children().html(CC[j])
//
//     }
// }
for(var i=0;i<1;i++){
   	$('.resource-content .resource-parent').eq(i).children().first().children().children().children().html('容器'+(i+1))
    for(var j=0;j<2;j++){
        $('.resource-content .resource-parent').eq(i).children('.resource-children').eq(j).children().eq(0).children().children().children().html('卡'+(j+1))

    }
}