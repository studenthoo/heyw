/***
	* ----------------------------------------------------------------------------
  * js Document public js Start 
	* Author: DistantSound
	* ----------------------------------------------------------------------------
	* 参数说明： 
	*	easing                缓动效果
	* effect                动画效果
	* autoPlay              自动运行
	* interTime ,delayTime  毫秒
	*	defaultIndex          默认的当前位置索引0
	* defaultPlay           默认是否执行效果
	* mainCell              切换元素的包裹层对象
  * titCell               鼠标的触发元素对象
***/

$(function() {
	
        if (!placeholderSupport()) {
                $("[placeholder]").focus(function() {
                        var input = $(this);
                        if (input.val() == input.attr("placeholder")) {
                                input.val("");
                                input.removeClass("placeholder");
                        }
                }).blur(function() {
                        var input = $(this);
                        if (input.val() == "" || input.val() == input.attr("placeholder")) {
                                input.addClass("placeholder");
                                input.val(input.attr("placeholder"));
                        }
                }).blur();
        };
//*** select  -------------------------------------------------
        $(".reg-select-box").each(function() {
                $(this).find(".option").hide(), $(this).toggle(function() {
                        $(this).find(".option").show(), $(this).find(".stat-op li").on("click", function() {
                                var a = $(this).text();
                                $(this).parents(".reg-select-box").find(".select-txt").text(a), $(this).find(".option").hide();
                        });
                }, function() {
                        $(this).find(".option").hide();
                });
        }); 

        $(".select-box").each(function() {
                $(this).find(".option").hide(), $(this).hover(function() {
                        $(this).find(".option").show(), $(this).find(".stat-op li").click(function() {
                                var a = $(this).text();
                                $(this).parents(".select-box").find(".select-txt").text(a), $(this).find(".option").hide();
                        });
                }, function() {
                        $(this).find(".option").hide();
                });
        });  


//*** listview, list -------------------------------------------------                                                                      
        $(".lis-c-ul li").each(function() {
         		     $(this).addClass("lis-c-view");
         		     $(".lis-c-dl").hide();
        });                    
        $(".btn-view").on("click", function() {
        				$(".lis-c-ul li").each(function() {
                				$(this).removeClass("lis-c-view");
                				$(this).addClass("lis-c-list");
        				}); 
        				$(".btn-view").hide();
        				$(".btn-list, .lis-c-dl").show();
        });   
        $(".btn-list").on("click", function() {
        				$(".lis-c-ul li").each(function() {
                				$(this).removeClass("lis-c-list");
                				$(this).addClass("lis-c-view");
        				}); 
        				$(".btn-list, .lis-c-dl").hide();
        				$(".btn-view").show();
        });             
   
			  $(".lis-ctshow").on("click", function () {
				 	 			$(".lis-ct").slideToggle(500);
			  });
	$(".slide-tab").slide({
		trigger:"click"
	});
//*** left menu,  left menu Scroll-------------------------------------------------
				$(".l-aside").width(200);
			  $(".lift-menu").addClass("side-menu");


					$("#side-menus").niceScroll({
						cursorcolor: "#829bb9",
						cursoropacitymax: 1,
						touchbehavior: false,
						cursorwidth: "4px",
						cursorborder: "4",
						cursorborderradius: "0",
						cursorminheight: 32,
						railpadding:{
							right:2
						},
						autohidemode: false ,
						background: "#49586d"
					});


				$(".l-sidemenu").toggle(function() {
				        $(".l-aside").width(50);
//				        $(".l-aside").animate({width:'50'},500);
				        $(".lift-menu").removeClass("side-menu").addClass("side-menu-s");
				}, function() {
				        $(".l-aside").width(200);
//				        $(".l-aside").animate({width:'200'},500);
				        $(".lift-menu").addClass("side-menu").removeClass("side-menu-s");
				});
				$(".xitong-h1").toggle(function() {
					$(this).addClass('current-la').siblings().removeClass('current-la')
					$(this).next(".side-div").slideDown(500)

				}, function() {
                    $(this).removeClass('current-la')
					$(this).next(".side-div").slideUp(500)
				});
				// $(".side-h1").on("click", function() {
				// 	      $(".side-h3").removeClass("current-lc");
				// 	      $(".side-h2").removeClass("current-lb");
				//         $(".side-h1").removeClass("current-la");
				//         $(this).addClass("current-la");
				//         if($(this).children().children('span').text()=='模型训练'){
				//         		$('.side-div').slideToggle(500)
				//         }
				//         else{
				//         	$('.side-div').slideUp(500)
				//         }
				//
				// });
				// $(".side-h2").toggle(function() {
				//         $(this).next(".side-ul").animate({height:"toggle",opacity:"toggle"}, "slow");
				// }, function() {
				//         $(this).next(".side-ul").animate({height:"toggle",opacity:"toggle"}, "slow");
				// });		
				$(".side-h2").on("click", function() {
				        // $(".side-h3").removeClass("current-lc");
				        $(".side-h2").removeClass("current-lb");
				        $(this).addClass("current-lb");       
				});
				// $(".side-h3").on("click", function() {
				//         $(".side-h3").removeClass("current-lb");
				//         $(".side-h3").removeClass("current-lc");
				//         $(this).addClass("current-lc");
				// }); 
				
				
//*** filter  -------------------------------------------------		 
        $(".filter-div").each(function() {
                var a = "\u5C55\u5F00+";
                var b = "\u6536\u8D77-";
                $(this).find(".filter-morel").text(a);
                $(".filter-list").find(".sort-s:gt(11)").hide();                   
                $(this).find(".filter-currentr");
                if ($(this).find(".filter-currentr").length > 0) {
                        $(this).addClass("filter-currentr");
                } else {
                        $(this).find(".sort-s:first").addClass("filter-currentr");
                }
                if ($(this).find(".sort-s").length > 11) {
                        $(this).find(".filter-morel").show();
                } else {
                        $(this).find(".filter-morel").hide();
                }
                $(".sort-s").hover( function() {
                     $(this).addClass("filter-bgcurrentr");
                }, function() {
                        $(this).removeClass("filter-bgcurrentr");
                }); 
                $(this).find(".sort-s").on("click", function() {
                        $(this).addClass("filter-currentr").siblings().removeClass("filter-currentr");
                });
                $(this).find(".filter-morel").toggle(function() {
                        $(this).parent().find(".sort-s:gt(11)").slideDown();
                        $(this).parent().find(".filter-morel").text(b);
                }, function() {
                        $(this).parent().find(".sort-s:gt(11)").slideUp();
                        $(this).parent().find(".filter-morel").text(a);
                });
        });
//*** mask newdataset-popup   ------------------------------------------------ 
        $(".new-dataset-popup").on("click", function() {
                $(".mask-box").fadeIn(300);
                $(".mask-newdataset-popup").slideDown(350);
        });
        $(".popup-close").on("click", function() {
                $(".mask-box").fadeOut(300);
                $(".mask-newdataset-popup").slideUp(350);
        });                      
//*** CPU GPU  memory meter------------------------------------------------                
// 				$(".cpu-meter").jQMeter({
// 				    goal:"100",
// 				    raised:"85",
// 				    orientation:"vertical",
// 				    bgColor:"#dfe6ea",
// 				    barColor:"#00b5b8",
// 				    width:"100%",
// 				    height:"24px"
// 				});
// 				$(".cpu-memory-meter").jQMeter({
// 				    goal:"100",
// 				    raised:"60",
// 				    orientation:"vertical",
// 				    bgColor:"#dfe6ea",
// 				    barColor:"#ff6275",
// 				    width:"100%",
// 				    height:"24px"
// 				});
// 				$(".gpu-meter").jQMeter({
// 				    goal:"100",
// 				    raised:"25",
// 				    orientation:"vertical",
// 				    bgColor:"#dfe6ea",
// 				    barColor:"#fc7d46",
// 				    width:"100%",
// 				    height:"24px"
// 				});
// 				$(".gpu-memory-meter").jQMeter({
// 				    goal:"100",
// 				    raised:"90",
// 				    orientation:"vertical",
// 				    bgColor:"#dfe6ea",
// 				    barColor:"#10c888",
// 				    width:"100%",
// 				    height:"24px"
// 				});
// 				$(".gpu-memory-meter").jQMeter({
// 				    goal:"100",
// 				    raised:"90",
// 				    orientation:"vertical",
// 				    bgColor:"#dfe6ea",
// 				    barColor:"#10c888",
// 				    width:"100%",
// 				    height:"24px"
// 				});
//				进度条 数据管理训练集
// 				$(".preview-dataset-meter").jQMeter({
// 				    goal:"100",
// 				    raised:"60",
// 				    orientation:"vertical",
// 				    bgColor:"#dfe6ea",
// 				    barColor:"#00b5b8",
// 				    width:"100%",
// 				    height:"40px"
// 				});
//*** 训练集 验证集 ------------------------------------------------ 
     $(".dataset-view").slide({mainCell:".bd ul",autoPlay:false,trigger:"click"});
        $(".lis-tl-hdli").on("click", function () {
				    $(".lis-tview-yz,.lis-tview-xl").hide();
			  });
			  $(".showDataset-xl").on("click", function () {
			  				$(".lis-tview-xl").children().children().attr('src',$('.url_i1').text())
				  			$(".lis-tview-xl").show();
				  			$(".lis-tview-yz").hide();
			  });
			  $(".showDataset-yz").on("click", function () {
			  	console.log(1)

			  				$(".lis-tview-yz").children().children().attr('src',$('.url_i2').text())
				  			$(".lis-tview-yz").show();
				   			$(".lis-tview-xl").hide();
			  });
			  
//新建分类,选择文本			  
//$('.input_file').on('change',function(){
//
//	$('.input_file_text').val($(this).val())
//	$('.input_file_text').val(e.currentTarget.files[0].name)
//})
			  
//*** 独立验证图像目录  dataManage-NewdatasetModify  ------------------------------------------------ 	
		    $(".lis-nlcheckshow").on("ifChecked", function(event) {
		         $(".lis-nl-hide").show();
		    });
		    
		    $(".lis-nlcheckshow").on("ifUnchecked", function(event) {
		         $(".lis-nl-hide").hide();
		    });    
		 
 
//*** 验证集目录是否单独隔离   dataManage-Newdataset-ImgeClass   图像文件  文本文件------------------------------------------------ 	
		    $(".lis-slcheck-img-show-a").on("ifChecked", function(event) {
		         $(".lis-sl-img-hide-a").show();
		    });
		    $(".lis-slcheck-img-show-a").on("ifUnchecked", function(event) {
		         $(".lis-sl-img-hide-a").hide();
		    });    
 		    $(".lis-slcheck-img-show-b").on("ifChecked", function(event) {
 		         $(".lis-sl-img-hide-b").show();
 		    });
 		    $(".lis-slcheck-img-show-b").on("ifUnchecked", function(event) {
 		         $(".lis-sl-img-hide-b").hide();
 		    }); 

//*** 独立验证图像目录  dataManage-NewdatasetModify-Segmentation ------------------------------------------------ 	
 		    $(".lis-olcheck-img-show").on("ifChecked", function(event) {
 		         $(".lis-ol-img-hide").show();
 		    });
 		    
 		    $(".lis-olcheck-img-show").on("ifUnchecked", function(event) {
 		         $(".lis-ol-img-hide").hide();
 		    });  						    
                                                                          
}); 
function placeholderSupport() {return "placeholder" in document.createElement("input");};

// 自动补全
// $(".explanation-tooltip").tooltip();
//
// window.onload = function () {
//     $('.autocomplete_path').autocomplete({
//        serviceUrl: '/autocomplete/path',
//        formatResult: function (suggestion, currentValue)
//        {
//             function baseName(str)
//             {
//                var base = new String(str).substring(str.lastIndexOf('/') + 1);
//                return base;
//             }
//             return baseName(suggestion.value);
//         },
//         minChars: 0
//     });
//     $(".autocomplete_path").removeAttr("autocomplete");
// };


