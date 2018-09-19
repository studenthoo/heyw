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
			['TensorFlow', 160],
			['Torch', 60],
			['Caffe', 90]

		]
var color3=['#fe6375', '#2674b6', '#03ded6', '#acacac','#e5e6e8']
round_fun("#round1",arr3,'12',color3,'模型');


var arr4=[
			['完成', '1'],
			['错误', '0'],
			['运行中', '0'],
			['未提交', 1]
		]
var color4=['#0dc999', '#bbcdd9', '#ff6276', '#ababab','#e5e6e8']
//	round_fun("#mychart-d",arr4,{{sum_graph[3]|length}},color4,'作业');
round_fun("#round2",arr4,'2',color4,'作业');


