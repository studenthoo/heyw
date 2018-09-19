// function tiao(url,arr1,arr2,color1){
// 	        c3.generate($.extend({
//             bindto: url,
// //          图例样式
//             legend: {show: false},//隐藏图例
//              color: {
//        			 pattern:color1
//        		},
//         },
//          {'data': {'type': 'bar',
// //              		数据
//                 		'columns':arr1},
//                 		'axis': {
//                 			'x': {
//                 					'type': 'category',
// //              					单个条形备注信息
//                 					'categories':arr2 ,
//                 					tick: {
// 										 count: 1
// 			                   	 },
//                 			}
//                 		}
//                 }
//        ));
//  $('.tick').first().css('display','none')
//	console.log($(url).children('svg').children().eq(1).children().eq(3).children().last())
//	$(url).children('svg').children().eq(1).children().eq(3).children('g').css('display','none')
//$('.tick').first().css('display','none')
//}

// var arr1=[['Count', 5057, 4699, 4598, 4469, 4462, 4442, 4439, 4388, 4382, 4066,5057, 4699, 4598, 4469, 4462, 4442, 4439, 4388, 4382, 4066]]
// var arr2=['1', '7', '3', '2', '9', '0', '6', '8', '4', '5']
// var color1=['#00b5b8']
// var color2=['#ff6376']
// tiao('#mychart-c1',arr1,arr2,color1)
// tiao('#mychart-c2',arr1,arr2,color2)
// $('#mychart-c1 .tick').first().css('display','none')
// $('#mychart-c2 .tick').first().css('display','none')

// 进度条
// 	 $(document).ready(function() {
// 	 	 namespace = '/test';
// 	 	  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
//             // socket.on('connect', function() {
//             //     socket.emit('my_event', {data: 'I\'m connected!'});
//             // });
//
// 		socket.on('task update', function (msg) {
// 			var status_selector = "#"+msg['task']+"-status";
// 			if (msg['update'] == 'progress') {
// 				if(msg['task'] == 'task-create_db-train'){
// 					$(".preview-dataset-meter").jQMeter({
// 				    goal:"100",
// 				    raised:msg['percentage'] + '%',
// 				    orientation:"vertical",
// 				    bgColor:"#dfe6ea",
// 				    barColor:"#00b5b8",
// 				    width:"100%",
// 				    height:"40px"
// 				});
// 				}
//
//       	  }
// 		}
// 	 	    // socket.on('my_response', function(msg) {
//             //     console.log(msg.vvv)
// 				// $(".preview-dataset-meter").jQMeter({
// 				//     goal:"100",
// 				//     raised:msg.vvv,
// 				//     orientation:"vertical",
// 				//     bgColor:"#dfe6ea",
// 				//     barColor:"#00b5b8",
// 				//     width:"100%",
// 				//     height:"40px"
// 				// });
//             // });
// 	 }