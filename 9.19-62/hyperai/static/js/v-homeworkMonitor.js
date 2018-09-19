$(function(){
    // 顶部 icon
    $(".l-sidemenu").on("click",function(){
        if ($(".left-menu").width() == 200) {
            $("aside").width(50)
            $(".left-menu").width(50)
            $(".left-menu .list").find("span").css("display","none")
//						$(".left-menu .list").css("height","50px")
//						$(".left-menu .list a").css("height","50px")
            $(".left-menu .list a").find("i").css("padding-top","30px")
            $(".train-list").hide()
        } else{
            $("aside").width(200)
            $(".left-menu").width(200)
            $(".left-menu .list").find("span").css("display","inline-block")
//						$(".left-menu .list").css("height","80px")
//						$(".left-menu .list a").css("height","80px")
            $(".left-menu .list a").find("i").css("padding-top","20px")
        }
    });
    // 左侧菜单栏
    $(".list").on("click",function(){
        $(this).find("a").addClass("current-la");
        $(this).siblings(".list").find("a").removeClass("current-la");
    });


    // 左侧菜单栏滚动条
    $("#left-list").niceScroll({
        cursorcolor: "#829bb9",
        cursoropacitymax: 1,
        touchbehavior: false,
        cursorwidth: "4px",
        cursorborder: "4",
        cursorborderradius: "0",
        cursorminheight: 32,
        railpadding:{
            right:0
        },
        autohidemode: false,
        background: "#49586d"
    });
    // 顶部右侧下拉菜单
    $(".select-box").hover(function(){
        $(this).find(".option").show();
        $(this).find(".option ul a").on("click",function(){
            var txt = $(this).text();
            $(this).parents(".select-box").find("span").text(txt);
        })
        $(this).find(".select-top i").css({"color": "#00B5B8","transition": "0.4s","transform": "rotateZ(180deg)"});
        $(this).find(".select-top span").css("color","#00B5B8");
    },function(){
        $(this).find(".option").hide()
        $(this).find(".select-top i").css({"color": "#2c3850","transition": "0.4s","transform": "rotateZ(0deg)"});
        $(this).find(".select-top span").css("color","#2C3850");
    });

////代码后置
    $(window).bind("load", function () {
        $(".l-sidemenu").on("click", function() {
            c3_a(numm);
            // c3_b(numm2);
        });
    });

})