"use strict";


(function($) {

	"use strict";

	var fullHeight = function() {

		$('.js-fullheight').css('height', $(window).height());
		$(window).resize(function(){
			$('.js-fullheight').css('height', $(window).height());
		});

	};
	fullHeight();

})(jQuery);

var mainbody = $('body');

$(document).ready( function(){    
    /* laoder script */
	setTimeout(function () {
		$(".loader-logo").fadeOut();
	}, 3000)


    $('.vh-full').css('height', ($(window).outerHeight() - $('footer > div').outerHeight()) );
    $('.vhi-full').css('height', $(window).outerHeight()- $('header').outerHeight() );

  	/* Sidebar toggle script */
	$('#sidebar-left').on('click', function (e) {
         e.stopPropagation();
		mainbody.toggleClass('menuleft-open');
		$(this).toggleClass("active");
	});
	$('#sidebar-right').on('click', function (e) {
         e.stopPropagation();
		mainbody.toggleClass('menuright-open');
		$(this).toggleClass("active");
	});

	/* Floating label */
	$('.float-label .form-control[placeholder]').each(function () {
		if ($(this).attr('placeholder').length > 0) {
			$(this).addClass('active');
		}
	});
	$('.float-label .form-control[value]').each(function () {

		if ($(this).val.length > 0) {

			$(this).addClass('active');
		}
	});
	$('.float-label .form-control').on('blur', function () {

		if ($(this).val().length > 0) {
			$(this).addClass('active');
		} else {
			if ($(this)[0].hasAttribute('placeholder') === true) {
				if ($(this).attr('placeholder').length > 0) {
					$(this).addClass('active');
				} else {
					$(this).removeClass('active');
				}
			} else {
				$(this).removeClass('active');
			}
		}
	});

    /* url  navigation active */
	var url = window.location;
	function menuitems() {
		var element = $('#side-menu li a').filter(function () {
			return this.href == url;
		}).addClass('active').parent("li").addClass('active').closest('.nav').slideDown().addClass('in').parent().addClass('show').closest('.nav').slideDown().addClass('in').parent().addClass('show');
	}
	menuitems();
	function menuitems2() {
		var element = $('.navbar-nav li a').filter(function () {
			return this.href == url;
		}).addClass('active').parent("li").addClass('active').closest('.nav').slideDown().addClass('in').parent().addClass('show').closest('.nav').slideDown().addClass('in').parent().addClass('show');
	}
	menuitems2();

	$('#side-menu li a:not(.menudropdown)').on('click', function () {
		$(this).addClass('active').parent("li").addClass('active').closest('.nav').slideDown().addClass('in').parent().addClass('show').closest('.nav').slideDown().addClass('in').parent().addClass('show');
	});
	$('#side-menu li a.menudropdown').on('click', function (e) {
        e.stopPropagation();
		if ($(this).parent().hasClass('show') !== true) {
			$('#side-menu li a.menudropdown').next().slideUp().removeClass('in').parent().removeClass("show");
			$(this).next().slideToggle().toggleClass('in').parent().toggleClass('show');
		} else {
			$(this).next().slideToggle().toggleClass('in').parent().toggleClass('show');
		}
	});


	/* Theme customization panel script */
	$("#color-setting").on('click', function (e) {
        e.stopPropagation();
		mainbody.toggleClass('menuright-open');
		$('#sidebar-right').toggleClass('active');        
		$('.sidebar .nav-tabs a[href="#setting"]').tab('show')
	});
	
    if($.type($.cookie("themecolor")) != 'undefined' && $.cookie("themecolor") != ''){
        var linkurl =$('#theme')
        $('head').append("<link id='theme' rel='stylesheet' href='"+$.cookie("themecolor")+"' type='text/css'>");
        $('.theme-color input[type="radio"]').prop( "checked",false);
        $( "label[data-title='"+$.cookie("themecolor")+"']" ).prev().prop( "checked",true);
        setTimeout(function(){             
            linkurl.remove();
        }, 1500);
	}
    
	$('.theme-color input[type="radio"]').on('click', function () {        
            $.cookie("themecolor", $(this).next().attr('data-title'), { expires: 7 });
     	    var linkurl =$('#theme')
            $('head').append("<link id='theme' rel='stylesheet' href='"+$(this).next().attr('data-title')+"' type='text/css'>");
           $(".loader-logo").show();
            setTimeout(function(){
                $(".loader-logo").fadeOut();
                linkurl.remove();
            }, 1500);
	});
	
	if($.type($.cookie("sidebarimgrepeat")) != 'undefined' && $.cookie("sidebarimgrepeat") != ''){
		$('body .wrapper > .sidebar').css({ 'background-image': 'url(' + $.cookie("sidebarimgrepeat") + ')', 'background-repeat': 'repeat', 'background-size': 'auto' });        
        $('.sidebar-image input[type="radio"]').prop( "checked",false);
		$( "label[data-title='"+$.cookie("sidebarimgrepeat")+"']" ).prev().prop( "checked",true);
	}
       if($.type($.cookie("sidebarimg")) != 'undefined' && $.cookie("sidebarimg") != ''){
		$('body .wrapper > .sidebar').css({ 'background-image': 'url(' + $.cookie("sidebarimg") + ')', 'background-repeat': 'no-repeat', 'background-size': '100%' });        
        $('.sidebar-image input[type="radio"]').prop( "checked",false);
		$( "label[data-title='"+$.cookie("sidebarimg")+"']" ).prev().prop( "checked",true);
	}
    
	$('.sidebar-image input[type="radio"]').on('click', function () {        
		if ($(this).hasClass('bg-repeat') === true) {
	            $.cookie("sidebarimgrepeat",  $(this).next().attr('data-title'), { expires: 7 });
			$.removeCookie('sidebarimg', { path: '/' });
        	    $('body .wrapper > .sidebar').css({ 'background-image': 'url(' + $(this).next().attr('data-title') + ')', 'background-repeat': 'repeat', 'background-size': 'auto' });
		} else {
	            $.cookie("sidebarimg",  $(this).next().attr('data-title'), { expires: 7 });
        	    $.removeCookie('sidebarimgrepeat', { path: '/' });
		    $('body .wrapper > .sidebar').css({ 'background-image': 'url(' + $(this).next().attr('data-title') + ')', 'background-repeat': 'no-repeat', 'background-size': '100%' });
		}
	});


	
	/* Dropdown center */
	$('.dropdown-menu-center').prev('.dropdown-toggle').on('click', function () {
		$(this).next('.dropdown-menu-center').css({ 'top': $(this).height(), 'margin-left': - (($(this).next('.dropdown-menu-center').outerWidth() / 2) - $(this).parent().width() / 2) })
	});
    
        /* navbar top margin */
    $('.navbar-collapse').css({'top': $('body .wrapper > header').outerHeight() });
    $('body .wrapper .sidebar').css({'padding-top': $('body .wrapper > header').outerHeight() });


    /* padding bottom */
	if (mainbody.hasClass('fixed-header') === true) {		
		$('body .wrapper').css('padding-top', $('body .wrapper > header').outerHeight() )
		mainbody.css('padding-bottom', $('body > .footer').outerHeight() )
	} else {
		$('body .wrapper').css('padding-top', '0');
        mainbody.css('padding-bottom', '0' )
	}

   
    /* hide menu on clicking out side sidebar and clicking on body */
    mainbody.on('click', function(e){ 
        if(mainbody.hasClass('menuleft-open') == true ){
            if(e.target.className !== 'sidebar' && e.target.id !== 'sidebar-left' && $(e.target).parents('.sidebar').length == 0 ){
                mainbody.removeClass('menuleft-open');
                $('#sidebar-left').removeClass('active');
            }
        }else if(mainbody.hasClass('menuright-open') == true ){
            if(e.target.className !== 'sidebar' && e.target.id !== 'sidebar-right' && $(e.target).parents('.sidebar').length == 0 ){
                mainbody.removeClass('menuright-open');
                $('#sidebar-right').removeClass('active');
            }
        }
    });
   
    
});
$(window).on("load", function () {
        $(".loader-logo").fadeOut();


        /*cicular progress sidebar home page */
        $('.progress_profile').circleProgress({
            fill: "#5ba0ff",
            /*fill: {gradient: ["#2ec7cb", "#6c8bef"]},*/
            lineCap: 'butt'
        });

        $('.progress_profile_file').circleProgress({
            fill: "#ffffff",
            /*fill: {gradient: ["#2ec7cb", "#6c8bef"]},*/
            lineCap: 'butt'
        });

        $('.progress_profile-sm').circleProgress({
            fill: "#5ba0ff",
            /*fill: {gradient: ["#2ec7cb", "#6c8bef"]},*/
            lineCap: 'butt'
        });

        /* Sparklines can also take their values from the first argument   passed to the sparkline() function */
        var myvalues = [10, 8, 5, 7, 4, 2, 8, 10, 8, 5, 6, 4, 1, 7, 4, 5, 8, 10, 8, 5, 6, 4, 4];
        $('.dynamicsparkline').sparkline(myvalues, { type: 'bar', width: '100px', height: '20', barColor: '#8596ae', barWidth: '2', barSpacing: 2 });
        $('.dynamicsparkline2').sparkline(myvalues, { type: 'bar', width: '100px', height: '20', barColor: '#ffffff', barWidth: '2', barSpacing: 2 });
        $('.dynamicsparkline3').sparkline(myvalues, { type: 'bar', width: '100%', height: '30', barColor: '#8596ae', barWidth: '2', barSpacing: 3 });

        /* Dropdown script */
        $('.dropdown-toggle').dropdown();

        /* Tooltip script */
        $('[data-toggle="tooltip"]').tooltip();

});

$(window).on("resize", function () {
        $('.vh-full').css('height', ($(window).outerHeight() - $('footer > div').outerHeight()) );
        $('.vhi-full').css('height', $(window).outerHeight()- $('header').outerHeight() );
        /* padding bottom */
        if (mainbody.hasClass('fixed-header') === true) {		
            $('body .wrapper').css('padding-top', $('body .wrapper > header').outerHeight() )
            mainbody.css('padding-bottom', $('body > .footer').outerHeight() )
        } else {
            $('body .wrapper').css('padding-top', '0');
            mainbody.css('padding-bottom', '0' )
        }
  
});


    
