// 基于准备好的dom，初始化echarts实例
var myChart1 = echarts.init(document.getElementById('mychart-1'));
var myChart2 = echarts.init(document.getElementById('mychart-2'));
var myChart3 = echarts.init(document.getElementById('mychart-3'));
var myChart4 = echarts.init(document.getElementById('mychart-4'));

// 指定图表的配置项和数据
var option1 = {
    title: {
//              text: '业务指标', //标题文本内容
    },
    toolbox: { //可视化的工具箱
        show: true,
//              feature: {
//                  restore: { //重置
//                      show: true
//                  },
//                  saveAsImage: {//保存图片
//                      show: true
//                  }
//              }
    },
    tooltip: { //弹窗组件
        formatter: "{a} <br/>{b} : {c}%"
    },
    series: [{
        name: '资源监控',
        type: 'gauge',
        detail: {
            formatter : "{score|{value}%}",
            offsetCenter: [0, "40%"],
//                   backgroundColor: '#FFEC45',
            height:30,
            rich : {
                score : {
//                           color : "white",
                    fontFamily : "微软雅黑",
                    fontSize : 14
                }
            }
        },
        data: [{value: 45, name: 'GPU使用率',fontSize:12}],
        axisLine : {
            show : true,
            lineStyle : { // 属性lineStyle控制线条样式
//                       color : [ //表盘颜色
//                           [ 0.5, "#DA462C" ],//0-50%处的颜色
//                           [ 0.7, "#FF9618" ],//51%-70%处的颜色
//                           [ 0.9, "#FFED44" ],//70%-90%处的颜色
//                           [ 1,"#20AE51" ]//90%-100%处的颜色
//                       ],
                width : 10//表盘宽度
            }
        },
        splitLine : { //分割线样式（及10、20等长线样式）
            length : 10,
            lineStyle : { // 属性lineStyle控制线条样式
                width : 2
            }
        },
    }]

};




var option2 = {
    title: {
//              text: '业务指标', //标题文本内容
    },
    toolbox: { //可视化的工具箱
        show: true,
//              feature: {
//                  restore: { //重置
//                      show: true
//                  },
//                  saveAsImage: {//保存图片
//                      show: true
//                  }
//              }
    },
    tooltip: { //弹窗组件
        formatter: "{a} <br/>{b} : {c}%"
    },
    series: [{
        name: '资源监控',
        type: 'gauge',
        detail: {
            formatter : "{score|{value}%}",
            offsetCenter: [0, "40%"],
//                   backgroundColor: '#FFEC45',
            height:30,
            rich : {
                score : {
//                           color : "white",
                    fontFamily : "微软雅黑",
                    fontSize : 14
                }
            }
        },
        data: [{value: 45, name: '显存使用率'}],
        axisLine : {
            show : true,
            lineStyle : { // 属性lineStyle控制线条样式
//                       color : [ //表盘颜色
//                           [ 0.5, "#DA462C" ],//0-50%处的颜色
//                           [ 0.7, "#FF9618" ],//51%-70%处的颜色
//                           [ 0.9, "#FFED44" ],//70%-90%处的颜色
//                           [ 1,"#20AE51" ]//90%-100%处的颜色
//                       ],
                width : 10//表盘宽度
            }
        },
        splitLine : { //分割线样式（及10、20等长线样式）
            length : 10,
            lineStyle : { // 属性lineStyle控制线条样式
                width : 2
            }
        },
    }]

};


var option3 = {
    title: {
//              text: '业务指标', //标题文本内容
    },
    toolbox: { //可视化的工具箱
        show: true,
//              feature: {
//                  restore: { //重置
//                      show: true
//                  },
//                  saveAsImage: {//保存图片
//                      show: true
//                  }
//              }
    },
    tooltip: { //弹窗组件
        formatter: "{a} <br/>{b} : {c}%"
    },
    series: [{
        name: '资源监控',
        type: 'gauge',
        detail: {
            formatter : "{score|{value}%}",
            offsetCenter: [0, "40%"],
//                   backgroundColor: '#FFEC45',
            height:30,
            rich : {
                score : {
//                           color : "white",
                    fontFamily : "微软雅黑",
                    fontSize : 14
                }
            }
        },
        data: [{value: 45, name: 'CPU使用率'}],
        axisLine : {
            show : true,
            lineStyle : { // 属性lineStyle控制线条样式
//                       color : [ //表盘颜色
//                           [ 0.5, "#DA462C" ],//0-50%处的颜色
//                           [ 0.7, "#FF9618" ],//51%-70%处的颜色
//                           [ 0.9, "#FFED44" ],//70%-90%处的颜色
//                           [ 1,"#20AE51" ]//90%-100%处的颜色
//                       ],
                width : 10//表盘宽度
            }
        },
        splitLine : { //分割线样式（及10、20等长线样式）
            length : 10,
            lineStyle : { // 属性lineStyle控制线条样式
                width : 2
            }
        },
    }]

};


var option4 = {
    title: {
//              text: '业务指标', //标题文本内容
    },
    toolbox: { //可视化的工具箱
        show: true,
//              feature: {
//                  restore: { //重置
//                      show: true
//                  },
//                  saveAsImage: {//保存图片
//                      show: true
//                  }
//              }
    },
    tooltip: { //弹窗组件
        formatter: "{a} <br/>{b} : {c}%"
    },
    series: [{
        name: '资源监控',
        type: 'gauge',
        detail: {
            formatter : "{score|{value}%}",
            offsetCenter: [0, "40%"],
//                   backgroundColor: '#FFEC45',
            height:30,
            rich : {
                score : {
//                           color : "white",
                    fontFamily : "微软雅黑",
                    fontSize : 14
                }
            }
        },
        data: [{value: 45, name: '内存使用率'}],
        axisLine : {
            show : true,
            lineStyle : { // 属性lineStyle控制线条样式
//                       color : [ //表盘颜色
//                           [ 0.5, "#DA462C" ],//0-50%处的颜色
//                           [ 0.7, "#FF9618" ],//51%-70%处的颜色
//                           [ 0.9, "#FFED44" ],//70%-90%处的颜色
//                           [ 1,"#20AE51" ]//90%-100%处的颜色
//                       ],
                width : 10//表盘宽度
            }
        },
        splitLine : { //分割线样式（及10、20等长线样式）
            length : 10,
            lineStyle : { // 属性lineStyle控制线条样式
                width : 2
            }
        },
    }]

};


// 使用刚指定的配置项和数据显示图表。
myChart1.setOption(option1);
myChart2.setOption(option2);
myChart3.setOption(option3);
myChart4.setOption(option4);

setInterval(function(){//把option.series[0].data[0].value的值使用random()方法获取一个随机数
    option1.series[0].data[0].value = (Math.random() * 100).toFixed(2) - 0;
    option2.series[0].data[0].value = (Math.random() * 100).toFixed(2) - 0;
    option3.series[0].data[0].value = (Math.random() * 100).toFixed(2) - 0;
    option4.series[0].data[0].value = (Math.random() * 100).toFixed(2) - 0;
    myChart1.setOption(option1, true);
    myChart2.setOption(option2, true);
    myChart3.setOption(option3, true);
    myChart4.setOption(option4, true);
}, 2000);