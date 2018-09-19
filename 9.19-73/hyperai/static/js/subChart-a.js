/***
	* ----------------------------------------------------------------------------
  * js Document Chart  js Start 
	* Author: DistantSound
	* 请参考官方 API
	* ----------------------------------------------------------------------------
***/
$(function() {

        var myChartA = echarts.init(document.getElementById("mychart-a"));
       
        /*** 应用场景 ***/
        myChartA.setOption({
                title:{
                        text:"应用场景",
                        x:"center",
                        subtext:"3",
                        itemGap:75,
                        textStyle:{
                                color:"#2c3850",
                                fontStyle:"normal",
                                fontFamily:"Microsoft YaHei",
                                fontWeight:"100",
                                fontSize:18
                        },
                        subtextStyle:{
                                color:"#2c3850",
                                fontStyle:"normal",
                                fontFamily:"Microsoft YaHei",
                                fontWeight:"300",
                                fontSize:24
                        }
                },
                tooltip:{
                        trigger:"item",
                        formatter:"{c}",
                        backgroundColor:"rgba(232,232,240,0.9);",
                        borderColor:"#dcdcdc",
                        borderWidth:1,
                        borderRadius:0,
                        padding:[ 0, 6 ],
                        enterable:true,
                        textStyle:{
                                fontSize:12,
                                color:"#727272",
                                Width:40
                        }
                },
                legend:{
                        type:"plain",
                        width:"auto",
                        itemWidth:12,
                        itemHeight:12,
                        padding:[ 5, 2 ],
                        borderRadius:[ 0 ],
                        bottom:5,
                        textStyle:{
                                color:"#999999",
                                fontStyle:"normal",
                                fontFamily:"Arial",
                                fontWeight:"100",
                                fontSize:12,
                                lineHeight:30
                        },
                        data:[ "图像", "文本", "语音" ]
                },
                series:[ {
                        type:"pie",
                        radius:[ "32%", "45%" ],
                        avoidLabelOverlap:false,
                        color:[ "#ff976a", "#0f9aee", "#10c888" ],
                        label:{
                                normal:{
                                        show:false,
                                        position:"center"
                                },
                                emphasis:{
                                        show:true,
                                        textStyle:{
                                                fontSize:"0",
                                                color:"#ffffff"
                                        }
                                }
                        },
                        labelLine:{
                                normal:{
                                        show:false
                                }
                        },
                        data:[ {
                                value:342554,
                                name:"图像"
                        }, {
                                value:432743,
                                name:"文本"
                        }, {
                                value:84432,
                                name:"语音"
                        } ]
                } ]
        });
       
       
        var myChartB = echarts.init(document.getElementById("mychart-b"));
       
        /*** 数据集 ***/
        myChartB.setOption({
                title:{
                        text:"数据集",
                        x:"center",
                        subtext:"2",
                        itemGap:75,
                        textStyle:{
                                color:"#2c3850",
                                fontStyle:"normal",
                                fontFamily:"Microsoft YaHei",
                                fontWeight:"100",
                                fontSize:18
                        },
                        subtextStyle:{
                                color:"#2c3850",
                                fontStyle:"normal",
                                fontFamily:"Microsoft YaHei",
                                fontWeight:"300",
                                fontSize:24
                        }
                },
                tooltip:{
                        trigger:"item",
                        formatter:"{c}",
                        backgroundColor:"rgba(232,232,240,0.9);",
                        borderColor:"#dcdcdc",
                        borderWidth:1,
                        borderRadius:0,
                        padding:[ 0, 6 ],
                        enterable:true,
                        textStyle:{
                                fontSize:12,
                                color:"#727272",
                                Width:40
                        }
                },
                legend:{
                        type:"plain",
                        width:"auto",
                        itemWidth:12,
                        itemHeight:12,
                        padding:[ 5, 2 ],
                        borderRadius:[ 0 ],
                        bottom:5,
                        textStyle:{
                                color:"#999999",
                                fontStyle:"normal",
                                fontFamily:"Arial",
                                fontWeight:"100",
                                fontSize:12,
                                lineHeight:30
                        },
                        data:[ "LMDB", "HDF5" ]
                },
                series:[ {
                        type:"pie",
                        radius:[ "32%", "45%" ],
                        avoidLabelOverlap:false,
                        color:[ "#ff976a", "#ffcc33" ],
                        label:{
                                normal:{
                                        show:false,
                                        position:"center"
                                },
                                emphasis:{
                                        show:true,
                                        textStyle:{
                                                fontSize:"0",
                                                color:"#ffffff"
                                        }
                                }
                        },
                        labelLine:{
                                normal:{
                                        show:false
                                }
                        },
                        data:[ {
                                value:342554,
                                name:"LMDB"
                        }, {
                                value:432743,
                                name:"HDF5"
                        } ]
                } ]
        });
       
        
        var myChartC = echarts.init(document.getElementById("mychart-c"));
       
        /*** 模型 ***/
        myChartC.setOption({
                title:{
                        text:"模型",
                        x:"center",
                        subtext:"3",
                        itemGap:75,
                        textStyle:{
                                color:"#2c3850",
                                fontStyle:"normal",
                                fontFamily:"Microsoft YaHei",
                                fontWeight:"100",
                                fontSize:18
                        },
                        subtextStyle:{
                                color:"#2c3850",
                                fontStyle:"normal",
                                fontFamily:"Microsoft YaHei",
                                fontWeight:"300",
                                fontSize:24
                        }
                },
                tooltip:{
                        trigger:"item",
                        formatter:"{c}",
                        backgroundColor:"rgba(232,232,240,0.9);",
                        borderColor:"#dcdcdc",
                        borderWidth:1,
                        borderRadius:0,
                        padding:[ 0, 6 ],
                        enterable:true,
                        textStyle:{
                                fontSize:12,
                                color:"#727272",
                                Width:40
                        }
                },
                legend:{
                        type:"plain",
                        width:"auto",
                        itemWidth:12,
                        itemHeight:12,
                        padding:[ 5, 2 ],
                        borderRadius:[ 0 ],
                        bottom:5,
                        textStyle:{
                                color:"#999999",
                                fontStyle:"normal",
                                fontFamily:"Arial",
                                fontWeight:"100",
                                fontSize:12,
                                lineHeight:30
                        },
                        data:[ "TensorFlow", "Torch", "Caffe" ]
                },
                series:[ {
                        type:"pie",
                        radius:[ "32%", "45%" ],
                        avoidLabelOverlap:false,
                        color:[ "#ff6275", "#2673b6", "#03ded6" ],
                        label:{
                                normal:{
                                        show:false,
                                        position:"center"
                                },
                                emphasis:{
                                        show:true,
                                        textStyle:{
                                                fontSize:"0",
                                                color:"#ffffff"
                                        }
                                }
                        },
                        labelLine:{
                                normal:{
                                        show:false
                                }
                        },
                        data:[ {
                                value:534,
                                name:"TensorFlow"
                        }, {
                                value:323,
                                name:"Torch"
                        }, {
                                value:532,
                                name:"Caffe"
                        } ]
                } ]
        });
       
       
        var myChartD = echarts.init(document.getElementById("mychart-d"));
        
        /*** 作业 ***/
        myChartD.setOption({
                title:{
                        text:"作业",
                        x:"center",
                        subtext:"4",
                        itemGap:75,
                        textStyle:{
                                color:"#2c3850",
                                fontStyle:"normal",
                                fontFamily:"Microsoft YaHei",
                                fontWeight:"100",
                                fontSize:18
                        },
                        subtextStyle:{
                                color:"#2c3850",
                                fontStyle:"normal",
                                fontFamily:"Microsoft YaHei",
                                fontWeight:"300",
                                fontSize:24
                        }
                },
                tooltip:{
                        trigger:"item",
                        formatter:"{c}",
                        backgroundColor:"rgba(232,232,240,0.9);",
                        borderColor:"#dcdcdc",
                        borderWidth:1,
                        borderRadius:0,
                        padding:[ 0, 6 ],
                        enterable:true,
                        textStyle:{
                                fontSize:12,
                                color:"#727272",
                                Width:40
                        }
                },
                legend:{
                        type:"plain",
                        width:"auto",
                        itemWidth:12,
                        itemHeight:12,
                        padding:[ 5, 2 ],
                        borderRadius:[ 0 ],
                        bottom:5,
                        textStyle:{
                                color:"#999999",
                                fontStyle:"normal",
                                fontFamily:"Arial",
                                fontWeight:"100",
                                fontSize:12,
                                lineHeight:30
                        },
                        data:[ "运行中", "暂停", "完成", "停止" ]
                },
                series:[ {
                        type:"pie",
                        radius:[ "32%", "45%" ],
                        avoidLabelOverlap:false,
                        color:[ "#10c888", "#bbcdd9", "#ff6376", "#ababab" ],
                        label:{
                                normal:{
                                        show:false,
                                        position:"center"
                                },
                                emphasis:{
                                        show:true,
                                        textStyle:{
                                                fontSize:"0",
                                                color:"#ffffff"
                                        }
                                }
                        },
                        labelLine:{
                                normal:{
                                        show:false
                                }
                        },
                        data:[ {
                                value:54534,
                                name:"运行中"
                        }, {
                                value:64743,
                                name:"暂停"
                        }, {
                                value:64222,
                                name:"完成"
                        }, {
                                value:12322,
                                name:"停止"
                        } ]
                } ]
        });
});                                                             