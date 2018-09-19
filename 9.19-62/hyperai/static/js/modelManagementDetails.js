$(function(){
// 展示可视化和统计


 $(".lis-zlcheckshow").on("click",function(event) {
 				var ck = $(".lis-zlcheckshow").prop("checked")
 				if (ck == true) {
 					$(".statistics-box").hide();
 					$(".chart-lbox").show();
 					
 				} else{
 					
 					$(".statistics-box").show();
 					$(".chart-lbox").hide();
 				}
             
                function drawHistogram(id, data) {
               		c3.generate({
               		bindto: id,
               		size: {height: 120},
            		data: {
                		columns: [
                    	['Count'].concat(data[0]),
                    	['Value'].concat(data[1]),
                	],
                	x: 'Value',
                	type: 'area-spline',
            		},
            		axis: {
                		x: {
//              		轴线备注
                    		label: {
                        	text: 'Value',
                        	position: 'outer-center',
                    		},
//                 		 刻度设置
                    		tick: {
                        	values: data[2],
                        	format: d3.format('.3g'),
                    		},
                    		padding: {left: 0},
                		},
                y: {
                    padding: {bottom: 0},
//             		     刻度削减
                     tick: {
					      count:1
//							outer: true
					    },
                     
                },
            },
            bar: {
               width: {ratio: 0.2}
            },
            padding: {left: 20, right: 20},
            legend: {hide: true},
        });
    }
drawHistogram("#mychart-a6", [[1291.0, 70818.0, 19000.0, 10716.0, 7321.0, 11342.0, 16714.0, 14199.0, 6611.0, 4045.0, 3532.0, 7903.0, 8045.0, 3700.0, 3536.0, 3055.0, 2367.0, 1230.0, 1109.0, 74.0], [-245.1999969482422, -225.60000610351562, -206.0, -186.39999389648438, -166.8000030517578, -147.1999969482422, -127.5999984741211, -108.0, -88.4000015258789, -68.80000305175781, -49.20000076293945, -29.600000381469727, -10.0, 9.600000381469727, 29.200000762939453, 48.79999923706055, 68.4000015258789, 88.0, 107.5999984741211, 127.19999694824219], [-255.0, -59.0, 137.0]]);
$("#mychart-a6 .tick:first").css("transform","translate(0px)")
});
console.log($('.model-changjing').text())
	if($('.model-changjing').text()=='image-sunnybrook' || $('.model-changjing').text()=='text-classification'){
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
	if($('.model-changjing').text()=='image-sunnybrook'){
		$('.custom-inference-form-i').eq(0).attr('id','custom-inference-form')
		$('.custom-inference-form-html-i').eq(0).attr('id','custom-inference-form-html')
	}
	else if($('.model-changjing').text()=='text-classification'){
		$('.custom-inference-form-html-i').eq(1).attr('id','custom-inference-form-html')
	}


})