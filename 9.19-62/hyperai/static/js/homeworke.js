// var c3_a=function(a){
//         c3.generate($.extend({
//             bindto: '#mychart-a2',
// //          title:{text:'zuoye',},//标题
//             axis: {
//                 x: {
//                     tick: {
//                         // 3 sig-digs
//                         format: function(x) { return Math.round(x * 1000) / 1000; },
// //                      fit: false,   //坐标位点偏移量
// //						count:7
// 						culling: {
// 						                    max: 7 //刻度显示数量
// 						                }
//                     },
//                     min: 0,
//                     padding: {left: 0},
//                      label: {
//                         text: '[轮数]',
//                         position: 'outer-right',
//                     },
//                 },
//                 y: {
//                     min: 0,
// //                  max:90,
//                     padding: {bottom: 0},
//                 },
//                 y2: {
//                     show: true,
// //                 		 最值
//                     min: 0,
//                     max: 100,
//                     padding: {top: 0, bottom: 0},
//                 },
//             },
//             color: {
//        			 pattern: ['#0e9aef', 'red', '#11c888', '#ababab','#e5e6e8']
//
//        		},
//        		point: {
// //     			参数点半径
// 			      r: 2,
// 			},
//             grid: {x: {show: true},
//             	y: {show: true}
//             },
//             legend: {position: 'bottom'},
//         },
//         {
//             data: {
// 		    	axes: {
// //		    		给data3额外添加Y轴
// 			        data3: 'y2' // ADD
// 			     },
// 		        columns: a
// 		    },
//             transition: {
//                 duration: 0,
//             },
//             subchart: {
//                 show: true,
//             },
//             zoom: {
//                 rescale: true,
//             },
//         }
//         ));
// }
// //	$('#mychart-a2').children().eq(0).children().eq(3).attr('transform','translate(-290,490)')
// var numm=[['损失率（训练）', 0, 87, 87],
// 	['准确率（验证）', 0, 87.14, 87.15],
// 	['损失率（验证）', 9.1, 9.2, 9.0, 9.1, 8.9, 10, 9.5,9.7, 9, 9.2, 9, 9.1, 9, 9.6, 9.5, 9.7,9.5, 9.6, 9.5,9.7, 9, 9.2, 9, 9.1, 9, 9.6, 9.5, 9.7,9.5, 9.6,9.7]
// ]
// c3_a(numm);
// var c3_b=function(a){
//         c3.generate($.extend({
//             bindto: '#mychart-a1',
// //          title:{text:'zuoye',},//标题
//             axis: {
//                 x: {
//                     tick: {
//                         // 3 sig-digs
//                         format: function(x) { return Math.round(x * 1000) / 1000; },
// //                      fit: false,//坐标位点偏移量
// 						culling: {
// 						         max: 7 //刻度显示数量
// 						}
//                     },
//                     min: 0,
//                     padding: {left: 0},
//                     label: {
//                         text: '[轮数]',
//                         position: 'outer-right',
//                     },
//                 },
//                 y: {
//                     min: 0,
// //                  max:90,
//                     padding: {bottom: 0},
//                },
//             },
//             color: {
//        			 pattern: ['#0e9aef', 'red', '#11c888', '#ababab','#e5e6e8']
//
//        		},
//        		point: {
// //     			参数点半径
// 			      r: 2,
// 			      select: {
// 				    r: 4
// 				  }
// 			},
//             grid: {x: {show: true},
//             	y: {show: true}
//             },
//             legend: {position: 'bottom'},
//         },
//         {
//             data: {
// 		        columns: a
// 		    },
//             transition: {
//                 duration: 0,
//             },
//         }
//         ));
// }
// var numm2=[['sample', 0, 87,50, 87, 30, 60,87, 90, 87, 77,60, 87,87, 87, 87, 76, 87, 50, 60, 90, 87, 87, 87,87, 80, 87, 87, 80, 80,70,80]]
// c3_b(numm2);
////代码后置
$(window).bind("load", function () {
	$(".l-sidemenu").on("click", function() {
					 c3_a(numm);
					     c3_b(numm2);    
					});
});



//var ww=10;
//setInterval(function(){
//	ww+=10
//	$(".length_i").animate({
//		'width':ww+'%'
//	},1000)
//	$(".length_i").html(ww+'%')
//	console.log(ww)
//	
//},1100)




			