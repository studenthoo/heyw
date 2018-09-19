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

    $(".side-h2").on("click", function() {
        
        $(".side-h2").removeClass("current-lb");
        $(this).addClass("current-lb");
    });











});
function placeholderSupport() {return "placeholder" in document.createElement("input");};



