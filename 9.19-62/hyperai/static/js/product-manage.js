//页码打印和筛选条件
    //	分页点击函数
    var yema=function(){
		$("#page").paging({
				pageNo:1,    //显示页面
				totalPage: 1,   //总页数
				totalSize: 300,
				callback: function(num) {
					console.log({
						num:num
					})
//					$.ajax({
//						type:"get",
//						url:"{num:num}",
//						async:true,
//						success:function(e){
//							
//						}
//					});
				}
		})
	}
yema()
//详情页面
$('.lis-e-view a').on('click',function(){
	window.location.href="product-monitoring.html"
})
