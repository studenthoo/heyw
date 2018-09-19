// public 
$(function(){
	
	//*** select  -------------------------------------------------
	        $(".select-box").each(function() {
	                $(this).find(".option").hide(), $(this).hover(function() {
	                        $(this).find(".option").show(), $(this).find(".stat-op li").on("click", function() {
	                                var a = $(this).text();
	                                $(this).parents(".select-box").find(".select-txt").text(a), $(this).find(".option").hide();
	                        });
	                }, function() {
	                        $(this).find(".option").hide();
	                });
	        }); 

	//*** left menu,  left menu Scroll-------------------------------------------------
			$(".l-aside").width(200);
			$(".lift-menu").addClass("side-menu");
 			$("#side-menu").niceScroll({
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
				$(".lift-menu").removeClass("side-menu").addClass("side-menu-s");
			}, function() {
				$(".l-aside").width(200);
				$(".lift-menu").addClass("side-menu").removeClass("side-menu-s");
			});
			$(".model-prc").toggle(function(){
				$(".side-div").slideDown("slow");
			},function(){
				$(".side-div").slideUp("slow");
			});
			$(".side-h2").toggle(function() {
				$(this).next(".side-ul").slideDown("slow");
			}, function() {
				$(this).next(".side-ul").slideUp("slow");
			});
			$(".side-h1").on("click", function() {
				$(".side-h3").removeClass("current-lc");
				$(".side-h2").removeClass("current-lb");
				$(".side-h1").removeClass("current-la");
				$(this).addClass("current-la");
			});		
			$(".side-h2").on("click", function() {
				$(".side-h3").removeClass("current-lc");
				$(".side-h2").removeClass("current-lb");
				$(this).addClass("current-lb");       
			});
			$(".side-h3").on("click", function() {
				$(".side-h3").removeClass("current-lb");
				$(".side-h3").removeClass("current-lc");
				$(this).addClass("current-lc");
			});    

});