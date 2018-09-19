let n1 = localStorage.getItem('sty')
let n2 = localStorage.getItem('sty1')
let n3 = localStorage.getItem('sty2')
let n4 = localStorage.getItem('sty3')
if(n1 == null) {
	$(".s-par").find('h4').eq(0).text('')
} else {

	$(".s-par").find('h4').eq(0).text(n1)
}
if(n2 == null) {
	$(".s-par").find('h4').eq(1).text('')
} else {

	$(".s-par").find('h4').eq(1).text(n2)
}
if(n3 == null) {
	$(".s-par").find('h4').eq(2).text('')
} else {

	$(".s-par").find('h4').eq(2).text(n3)
}
if(n4 == null) {
	$(".s-par").find('h4').eq(3).text('')
} else {

	$(".s-par").find('h4').eq(3).text(n4)
}