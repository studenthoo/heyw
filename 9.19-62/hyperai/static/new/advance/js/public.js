
$(document).ready(function(){
	

//*** left-menu scroll----------------------------------------
	$("#l-slider").niceScroll({
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
   

	$('.left-menu').on('click','li',function(){
		$(this).find('a').addClass('lc-menu')
		$(this).siblings().find('a').removeClass('lc-menu')
		
	})
	$('.left-menu .xtgl').on('click',function(){
//		$('this').find('a').find('.xiala').css('transform','rotate(0deg)!important')
		console.log('11')
		$('.xit-menu').slideToggle('fast')
	})
	
	
	
	
//	var page=function (a) {
//      $("#page").paging({
//          pageNo:1,    //显示页面
//          totalPage: a,   //总页数
//          totalSize: 300,
//          callback: function(num) {
//            
//
//          }
//      })
//  }
//page(2)
	
	 $('.check_all').on('click',function () {

        if($(this).is(':checked') == true){
        	console.log('111111111111111')
            $('.delete-icon').css('visibility','visible')
            $('.check_each').each(function () {
            	console.log('--')
                $(this).prop('checked',true)
            })
            $('.jobs_num').html($(":checkbox[name=subcheck]:checked").size())
        }else {
            $('.delete-icon').css('visibility','hidden')
            $('.check_each').each(function () {
//              $(this).removeAttr('checked','checked')
				$(this).prop('checked',false)
            })
            $('.jobs_num').html($(":checkbox[name=subcheck]:checked").size())

        }
    })
 
 $('.check_each').on('click',function () {
        $('.check_each').each(function () {
//            console.log($(":checkbox[name=subcheck]:checked").size())
            if($(":checkbox[name=subcheck]:checked").size() == 0){
                $('.delete-icon').css('visibility','hidden')
//              $('.check_all').removeAttr('checked','checked')
				$('.check_all').prop('checked',false)
                $('.jobs_num').html($(":checkbox[name=subcheck]:checked").size())
            }else{
                $('.delete-icon').css('visibility','visible')
                $('.jobs_num').html($(":checkbox[name=subcheck]:checked").size())
            }
        })
    })



   	
})
window.onload = function () {
    $('.autocomplete_path').autocomplete({
        serviceUrl: '/autocomplete/path',
        formatResult: function (suggestion, currentValue)
        {
            function baseName(str)
            {
                var base = new String(str).substring(str.lastIndexOf('/') + 1);
                return base;
            }
            return baseName(suggestion.value);
        },
        minChars: 0
    });
    $(".autocomplete_path").removeAttr("autocomplete");
};

