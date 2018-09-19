$(function(){
	//checkbox
	$(".lis-adcheck-show").on("ifChecked", function(event) {
 		      	$(".lis-adcheck-hide").show();
 	});
 	$(".lis-adcheck-show").on("ifUnchecked", function(event) {
 		        $(".lis-adcheck-hide").hide();
 	});
 		    
 	//自定义参数    
 	$(".customize-add").on("click", function() {
        customizeAdd(), $(".customize-addlis").each(function() {
            $(this) && $(this).find(".customize-remove").on("click", function() {
                $(this).parents(".customize-addlis").remove();
            }), $(this) && $(this).find(".customize-remove").on("click", function() {
                    $(this).children(".customize-addlis").remove();
                });
        });
    });
    $(".customize-remove").on("click", function() {
        $(this).parents(".customize-addlis").remove();
    });
})
function customizeAdd() {$(".lis-customizebox").append('<div class="c-box customize-addlis m-t15">'+'<input type="text" placeholder="Image1" class="f-l input-info bdr w-16-1 ml-12" />'+'<input type="text" placeholder="12444" class="f-l input-info bdr w-18 ml-12" />'+'<input type="text" placeholder="12444" class="f-l input-info bdr w-18 ml-12" />'+'<a href="#" class="f-r c-red customize-remove m-t5"> <i class="iconfont fz-20 plr-5"> &#xe638; </i></a>'+'</div>');};        