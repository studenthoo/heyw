//图表日志切换
$('.title').on('click','.train-btn',function(){
	console.log('-----')
	$(this).addClass('tab-color').siblings().removeClass('tab-color')
	if ($(this).html() == '训练监控') {
		$('.chart-box').show()
		$('.log-box').hide()
	} else{
		$('.log-box').show()
		$('.chart-box').hide()
		 $('.log-content')[0].scrollTop = $('.log-content')[0].scrollHeight
	}
})
