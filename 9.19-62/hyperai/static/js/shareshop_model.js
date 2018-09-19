// 页面交互
console.log(JSON.parse(localStorage.getItem('model')))
var content_all=null
$.ajax({
				type:'GET',
				url:'/store/get_models',
				data:JSON.parse(localStorage.getItem('model')),
				async:false,
				success:function (res) {
					console.log(res)
					content_all={'data':res,
							'job_id':JSON.parse(localStorage.getItem('model')).job_id
					}
					// local(JSON.stringify(res))
				}

		})
// var content_all=JSON.parse(localStorage.string)
		$('.name_d').text(content_all.data.model.name)
		$('.publish_user').text(content_all.data.model.publish_user)
		$('.create_time').text(content_all.data.model.create_time)
		$('.buy_num').text(content_all.data.model.buy_num)
		$('.apply_scenes').text(content_all.data.model.apply_scenes)
		$('.framework').text(content_all.data.model.framework)
		$('.network').text(content_all.data.model.network)
		$('.desc').text(content_all.data.model.desc)
		$('.accuracy').text(content_all.data.model.accuracy)
		$('.data_pl_xing_xing').attr('data-score',content_all.data.model.star)
		// console.log(content_all)
console.log(localStorage.getItem('data'))

// 评轮隐藏
$('.pl_content_all').children().css('display','none')

//分页
 var yema=function(a){
		$("#page").paging({
				pageNo:1,    //显示页面
				totalPage: a,   //总页数
				totalSize: 300,
				callback: function(num) {
					console.log({
						num:num,

					})
                    $.post('/store/get_model_comment',{'num':num,
							'id':content_all.data.model.id
                    },function (e) {
						console.log(e)
						$('.pl_content_all').children().css('display','none')
						for(var i=0;i<e.comments.length;i++){
							console.log(i)
							$('.pl_content_all').children().eq(i).css('display','block')
							$('.pl_content_i_h2').eq(i).html(e.comments[i].comment_name)
							$('.pl_content_i_xing').eq(i).attr('data-score',e.comments[i].comment_star)
							$('.pl_content_i_time').eq(i).html(e.comments[i].time)
							$('.pl_content_i_text').eq(i).html(e.comments[i].comment_content)
						}
                    })
				}
		})
	}






// 评论星星
//         $(".starscore-a").each(function() {
//                 var d, c;
//                 $.fn.raty.defaults.path = "/static/plugins/jqueryraty/img", d = $(this).find(".count-hint"),
//                 c = $(this).find(".star-score"), $(this).find(".star-score").raty({
//                         number:5,
//                         size:16,
//                         starOff:"star-off.png",
//                         starOn:"star-on.png",
//                         readOnly: true,
//                         cancel:false,
//                         targetType:"number",
//                         targetKeep:true,
//                         precision:false,
//                         score:function() {
//                                 return $(this).attr("data-score");
//                         }
//                 }), "" == c.text() && d.text("0"), "" == d.text() && d.text(+c.attr("data-score")),
//                 $(this).find("img").click(function() {
//                         d.text(+$(this).attr("alt"));
//                 });
//         });
//         $(".starscore-b").each(function() {
// 				var d, c, num;
// 				$.fn.raty.defaults.path = "/static/plugins/jqueryraty/img", d = $(this).find(".count-hint"),
// 				c = $(this).find(".star-score"), $(this).find(".star-score").raty({
// 						number: 5,
// 						size: 16,
// 						starOff: "star-off.png",
// 						starOn: "star-on.png",
// 						cancel: false,
// 						targetType: "number",
// 						targetKeep: true,
// 						precision: false,
// 						score: function() {
// 							num = parseInt($(this).attr("data-score"))
// 							return $(this).attr("data-score");
// 						},
// 						click:function(number){
// 							num = number
// 						}
// 				}), "" == c.text() && d.text("0"), "" == d.text() && d.text(+c.attr("data-score")),
// 				$(this).find("img").click(function() {
// 						d.text(+$(this).attr("alt"));
// //						console.log("-----",num)
// 				});
				//发表评论			
				$(".comment").on("click",function(){
					var txt = $(this).prev("textarea").val();
					var time = new Date();
					var year = time.getFullYear();
					var month = time.getMonth();
					var day = time.getDate();
					var hour = time.getHours();
					var minute = time.getMinutes();
					var second = time.getSeconds();
					if (month < 10) {
				    	month  = "0" + month
				    } else{
				    	month = month
				    }
				    if (day < 10) {
				    	day  = "0" + day
				    } else{
				    	day = day
				    }
				    if (hour < 10) {
				    	hour  = "0" + hour
				    } else{
				    	hour =  hour
				    }
				    if (minute < 10) {
				    	minute  = "0" + minute
				    } else{
				    	minute = minute
				    }
				    if (second < 10) {
				    	second  = "0" + second
				    } else{
				    	second = second
				    }
					// var comment_obj = {"star":num,"content":txt,"now_y":year,"now_m":month,"now_d":day,"now_h":hour,"now_mm":minute,"now_s":second}
					// console.log(comment_obj)
					yema(1)
					$.post('/store/model/comments/',{
							"content":txt,
							'id':content_all.data.model.id
							},function (e) {
								console.log('=======',e)
								$('.pl_num_all').html(e.comments.length+"条")
								yema(e.page_z)
								for(var i=0;i<e.comments.length;i++){
									$('.pl_content_all').children().eq(i).css('display','block')
									$('.pl_content_i_h2').eq(i).text(e.comments[i].comment_name)
									// $('.pl_content_i_xing').eq(i).attr('data-score',e.comments[i].comment_star)
									$('.pl_content_i_time').eq(i).text(e.comments[i].time)
									$('.pl_content_i_text').eq(i).text(e.comments[i].comment_content)
								}
					})
				$('.comment_content').val(' ')
				})
		// });
        // $(".btn-like").on("click", function () {
		//   					var a = parseInt($(this).find("b").text());
    		// 				$(this).find("b").text(a + 1);
		// 		});
//function customizeAdd() {$(".lis-customizebox").append('<div class="c-box customize-addlis m-t15">'+'<input type="text" placeholder="Image1" class="f-l input-info bdr w-16-1 ml-12" />'+'<input type="text" placeholder="12444" class="f-l input-info bdr w-18 ml-12" />'+'<input type="text" placeholder="12444" class="f-l input-info bdr w-18 ml-12" />'+'<a href="#" class="f-r c-red customize-remove m-t5"> <i class="iconfont fz-20 plr-5"> &#xe638; </i></a>'+'</div>');};        

// 返回顶部
$(".go-top").on("click",function(){
	$("article").scrollTop(0)
})

// 回复
// var div = $("<div class='reply-2 f-l'><div>")
// $("li").append(div)
// var s = $("<form action='#' class='reply f-l'><textarea class='content f-l c-gray bdr m-t15'></textarea><input type='button' value='回复' class='f-l bgc-Aqua c-white bgc-red-h btn-1 m-t20 m-r15 btn' style='border:none'/></form>")
// $(".btn-reply").parents(".bdr-b").append(s)
// $(".btn-reply").toggle(function(){
// 	$(this).parents(".bdr-b").siblings().find(".reply").css("display","none")
// 	$(this).parents(".bdr-b").find(".reply").css("display","block")
// },function(){
// 	$(this).parents(".bdr-b").find(".reply").css("display","none")
// })
// $(".btn").on("click",function(){
// 	var txt = $(this).siblings(".content").val()
// 	var time = new Date()
// 	var year = time.getFullYear()
// 	var month = time.getMonth()
// 	var day = time.getDate()
// 	var hour = time.getHours()
// 	var minute = time.getMinutes()
// 	var second = time.getSeconds()
// 	if (month < 10) {
//     	month  = "0" + month
//     } else{
//     	month = month
//     }
//     if (day < 10) {
//     	day  = "0" + day
//     } else{
//     	day = day
//     }
//     if (hour < 10) {
//     	hour  = "0" + hour
//     } else{
//     	hour =  hour
//     }
//     if (minute < 10) {
//     	minute  = "0" + minute
//     } else{
//     	minute = minute
//     }
//     if (second < 10) {
//     	second  = "0" + second
//     } else{
//     	second = second
//     }
// 	var doctime = $("<div class='reply-time'></div>").text(year + "-" + month + "-" + day + "  " + hour + ":" + minute + ":" + second)
// 	var doc = $("<div class='reply-content'></div>").text(txt)
//    	$(this).parent(".reply").siblings(".reply-2").append(doctime)
//    	$(this).parent(".reply").siblings(".reply-2").append(doc)
// 	$(".reply").hide()
// })

// 评论首页展示
$.get('/store/model/comments/?id='+content_all.data.model.id,function (e) {
		console.log(e)
		console.log(e.comments.length)
		$('.pl_num_all').html(e.comments.length+"条")
		yema(e.page_z)
		for(var i=0;i<e.comments.length;i++){
			console.log(e.comments[i].comment_star+':'+i)
			$('.pl_content_all').children().eq(i).css('display','block')
			$('.pl_content_i_h2').eq(i).html(e.comments[i].comment_name)
			// $('.pl_content_i_xing').eq(i).attr('data-score',e.comments[i].comment_star)
			$('.pl_content_i_time').eq(i).html(e.comments[i].time)
			$('.pl_content_i_text').eq(i).html(e.comments[i].comment_content)
			$('.pl_content_i_xing').eq(i).attr('data-score',e.comments[i].comment_star)
		}
    })




