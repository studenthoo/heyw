/***
	* ----------------------------------------------------------------------------
  * js Document Chart  js Start 
	* Author: DistantSound
	* 请参考官方 API
	* 学习监控 ,
	* ----------------------------------------------------------------------------
***/
$(function() {

        window.addEventListener("resize", function () {
                      option.chart.resize();
        });


        var myChartAA = echarts.init(document.getElementById("mychart-a1"));
        
        /*** 学习监控 ***/
				myChartAA.setOption({
				        title:{
				                text:"【轮数】",
				                x:"center",
				                bottom: 0,
				                textAlign: "center",
				                textStyle:{
				                        fontSize:14,
				                        fontFamily:"Microsoft YaHei",
				                        fontWeight:200
				                }
				        },
				        tooltip:{
				                trigger:"axis",
				                padding:[ 10, 10 ],
				                textStyle:{
				                        fontStyle:"normal",
				                        fontFamily:"Microsoft YaHei",
				                        fontWeight:"300",
				                        fontSize:14
				                },
				                axisPointer:{
				                        lineStyle:{
				                                color:"#ff6376",
				                                width:1,
				                                type:"solid"
				                        }
				                }
				        },
				        legend:{
				                type:"plain",
				                show:true,
				                left:"0",
				                itemGap:10,
				                width:"100%",
				                bottom:"0",
				                padding:[ 0, 60  ],
				                orient:"horizontal",
				        },
				        grid:{
				        	       top:"8%",
				                 left:"5%",
				                 right:"5%",
				                 bottom:"8%",
				                containLabel:true
				        },
				        xAxis:{
				                type:"category",
				                boundaryGap:false,
				                data:[ "0", "1", "2", "3", "4", "5", "6", "7", "8", "9" ],
				                splitLine:{
				                        show:true,
				                        lineStyle:{
				                                color:"#ccc",
				                                width:1
				                        }
				                },
				        },
				        yAxis:{
				                type:"value",
				                boundaryGap:false,
				                splitLine:{
				                        show:true,
				                        lineStyle:{
				                                color:"#cccccc",
				                                width:1
				                        }
				                },
				        },
				        series:[ {
				                name:"学习率",
				                type:"line",
				                color:[ "#0f9aee" ],
				                symbolSize:6,
				                data:[ 1800, 932, 201, 1200, 190, 330, 1810, 690, 380, 1210 ],
				               lineStyle:{
				                        normal:{
				                                width:2
				                        }
				               }
				        } ]
				});
 

        var myChartBB = echarts.init(document.getElementById("mychart-a2"));
        
        /*** 训练监控 ***/
				myChartBB.setOption({
				        title:{
				                text:"【轮数】",
				                x:"center",
				                bottom: 0,
				                textAlign: "center",
				                textStyle:{
				                        fontSize:14,
				                        fontFamily:"Microsoft YaHei",
				                        fontWeight:200
				                }
				        },
				        tooltip:{
				                trigger:"axis",
				                padding:[ 10, 10 ],
				                textStyle:{
				                        fontStyle:"normal",
				                        fontFamily:"Microsoft YaHei",
				                        fontWeight:"300",
				                        fontSize:14
				                },
				                axisPointer:{
				                        lineStyle:{
				                                color:"#ff6376",
				                                width:1,
				                                type:"solid"
				                        }
				                }
				        },
				        legend:{
				                type:"plain",
				                show:true,
				                left:"0",
				                itemGap:10,
				                width:"100%",
				                bottom:"0",
				                padding:[ 0, 60  ],
				                orient:"horizontal",
				                data:[ "损失率", "(验证) 准确率", "(验证) 损失率" ]
				        },
				        grid:{
				        	       top:"8%",
				                 left:"5%",
				                 right:"5%",
				                 bottom:"12%",
				                containLabel:true
				        },
				        xAxis:{
				                type:"category",
				                data:[ "0", "5", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55" ],
				                boundaryGap:false,
				                axisTick:{
				                        alignWithLabel:true
				                },
				                splitLine:{
				                        show:true,
				                        lineStyle:{
				                                color:"#ccc"
				                        }
				                }
				        },
				        yAxis:[ {
				                type:"value",
				                min:0,
				                max:2800,
				                position:"left",
				                axisLabel:{
				                        formatter:"{value}"
				                },
				                splitLine:{
				                        lineStyle:{
				                                color:"#ccc"
				                        }
				                }
				        }, {
				                type:"value",
				                min:0,
				                max:100,
				                position:"right",
				                offset:20,
				                axisLabel:{
				                        formatter:"{value}"
				                },
				                splitLine:{
				                        lineStyle:{
				                                color:"#ccc"
				                        }
				                }
				        } ],
				        series:[ {
				                name:"损失率",
				                type:"line",
				                smooth:true,
				                symbolSize:6,
				                data:[ "200", "1800", "1008", "1411", "1026", "1288", "1300", "800", "1100", "1000", "1118", "1322" ],
				                areaStyle:{
				                        normal:{
				                                color:new echarts.graphic.LinearGradient(0, 0, 0, 1, [ {
				                                        offset:0,
				                                        color:"rgba(23, 158, 239,0.4)"
				                                } ], false)
				                        }
				                },
				                itemStyle:{
				                        normal:{
				                                color:"#179eef"
				                        }
				                },
				                lineStyle:{
				                        normal:{
				                                width:1
				                        }
				                }
				        }, {
				                name:"(验证) 准确率",
				                type:"line",
				                smooth:true,
				                symbolSize:6,
				                data:[ "1200", "1400", "808", "811", "626", "488", "1600", "1100", "500", "300", "1998", "822" ],
				                areaStyle:{
				                        normal:{
				                                color:new echarts.graphic.LinearGradient(0, 0, 0, 1, [ {
				                                        offset:0,
				                                        color:"rgba(250, 116, 57, 0.4)"
				                                } ], false)
				                        }
				                },
				                itemStyle:{
				                        normal:{
				                                color:"#fa7439"
				                        }
				                },
				                lineStyle:{
				                        normal:{
				                                width:1
				                        }
				                }
				        }, {
				                name:"(验证) 损失率",
				                type:"line",
				                smooth:true,
				                symbolSize:6,
				                data:[ "1400", "1450", "2422", "845", "1446", "733", "436", "1443", "474", "966", "1454", "374" ],
				                areaStyle:{
				                        normal:{
				                                color:new echarts.graphic.LinearGradient(0, 0, 0, 1, [ {
				                                        offset:0,
				                                        color:"rgba(6, 194,129, 0.4)"
				                                } ], false)
				                        }
				                },
				                itemStyle:{
				                        normal:{
				                                color:"#06c281"
				                        }
				                },
				                lineStyle:{
				                        normal:{
				                                width:1
				                        }
				                }
				        } ]
				});

				$(".l-sidemenu").on("click", function() {
				     myChartAA.resize();
				     myChartBB.resize();
				});
});
                                                                  