$(".tab-btn1").on("click",function(){
	$(".form1").show();
	$(".form2").hide();
	$(this).addClass("tab-color").siblings().removeClass("tab-color")
})
$(".tab-btn2").on("click",function(){
	$(".form2").show();
	$(".form1").hide();
	$(this).addClass("tab-color").siblings().removeClass("tab-color")
})
$(".form2 .framework").on("click",".standard",function () {
	$(this).addClass("standard-color").siblings(".standard").removeClass("standard-color")
})
// function getFileName(path) {
// 	var pos1 = path.lastIndexOf("/");
// 	var pos2 = path.lastIndexOf("\\");
// 	var pos = Math.max(pos1,pos2);
// 	if (pos < 0){
// 		return path
// 	}else{
// 		return path.substring(pos + 1);
// 	}
// }
// $(".form-control").change(function(){
// 	console.log("----------")
// 	var str = $(this).val();
// 	var fileName = getFileName(str)
// 	$(this).parents("a").prev("input").val(fileName);
// })
// $(".tab-box").on("click",".tab_btn", function () {
// 	var tab_txt = $(this).text()
// 	console.log(tab_txt)
// 	$.post("/models/distributed/vip_log",{data: tab_txt},function () {
// 		console.log('--------')
//     })
// })