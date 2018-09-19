// //详情跳转
// var local=function (e) {
// 	localStorage.setItem(e)
// 	console.log(e)
// }
// var content_data=null
// $('.a_data').on('click',function(){
// 	window.location.href='/show/shop/dataset'
// 	var index_i=Number($('.a_data').index(this))
// 	$.get('/store/datasets',function (e) {
// 		post_id=e.dataset[index_i].id
//
// 		console.log({id:e.dataset[index_i].id,
// 					job_id:e.dataset[index_i].job_id
// 				})
// 		localStorage.clear()
// 		localStorage.setItem('data',JSON.stringify({id:e.dataset[index_i].id,
// 					job_id:e.dataset[index_i].job_id
// 				}))
// 		console.log(JSON.parse(localStorage.getItem('data')))
// 	})
// })
// var content_model=null
// $('.a_model').on('click',function(){
// 	window.location.href='/show/shop/model'
// 	var index_i=Number($('.a_model').index(this))
// 	$.get('/store/models',function (e) {
// 		console.log({id:e.model[index_i].id,
// 					job_id:e.model[index_i].job_id
// 				})
// 		localStorage.clear()
// 		localStorage.setItem('model',JSON.stringify({id:e.model[index_i].id,
// 					job_id:e.model[index_i].job_id
// 				}))
// 		console.log(JSON.parse(localStorage.getItem('model')))
// 	})
//
//
//
//
// })
// //返回顶部锚点
// $('.btn-4').on('click',function(){
// 	$('body').scrollTop(0)
// })

