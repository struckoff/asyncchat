function TimestampFormat(timestamp){
	time = new Date(timestamp*1000);
	h    = time.getHours();
	m    = time.getMinutes();
	s    = time.getSeconds();

	return (h>10?h:'0'+h) + '.' + (m>10?m:'0'+m) + '.' + (s>10?s:'0'+s);
}

host = window.location.hostname;
// if (host == 'localhost')
// 	{host+=':4042/';}
// else
// 	{host = 'ngrok.com:49689/';}
host+=':4042/';

ws = new WebSocket('ws://'+host);
ws.onopen = function() {
	console.log("Connection opened...");
	data = {
			'name'       : name_js_from,
			'token'      : token_js_from,
			'room'       : room_js_from,
			'room_token' : room_token_js_from,
			'type_msg'   : 'login'
		};
	console.log(data);
	ws.send(JSON.stringify(data));
    };
ws.onclose   = function() { console.log("Connection closed...");};
ws.error     = function(event) { console.log("Connection error..."+event);};
ws.onmessage = function(event) {
	data_json = $.parseJSON(event['data']);
	
	console.log(data_json);

	if (data_json['message'] || data_json['image']){

		var message_div = $('<div class = "message"></div>');
		var top_bar_message = '<span class = "top_bar_message"><span>From: <span class = "user_name '+((data_json['name']==name_js_from)?' self':'')+'">'+data_json['name']+'</span></span>';
		var message_time = TimestampFormat(data_json['time']);


		console.log(message_time);
		top_bar_message += '<span>Time: <span class = "message_time">'+message_time+'</span></span>';
		top_bar_message += '</span>';
		$(message_div).append(top_bar_message);
		var mes = "<p class='message"+((data_json['name']==name_js_from)?' self':'')+"'><span class = 'message expandable'>";
		if (data_json['message']){mes += data_json['message'];}
		mes += '</span>';
		if (data_json['image']){mes+='<a class = "message" href="'+data_json['image']+'" data-lightbox="example-2"><img src="'+data_json['image']+'" class = "message"></a>';}
		mes += "</p>";
		$(message_div).append(mes);
		$('#message').append(message_div);
	}
	if (data_json['user_list']){
		$('#user_list').html('');
		$.each(data_json['user_list'],function(key,val){
			$('#user_list').append('<span class = "user_list_item">'+key+':'+val+'</span>');
			if (val == name_js_from){$('.user_list_item').last().addClass('self');}
			});
		}
	if (data_json['error']){
		$('#error').prepend(data_json['error']);
		$('#error').foundation('reveal', 'open');
		console.log(data_json['error']);
	}
	};

$("#send").click(function(e){
	data = {
				'message' :$('#sending_message').val(),
				'type_msg':'message'
			};
	if (img){data['image'] = img; img = 0;}
	else {data['image'] = '';}
	ws.send(JSON.stringify(data));
	console.log(data);
	$('#sending_message').val('');
	$("#uploader").val('');
	e.preventDefault();
});

function readImage(input) {
    if ( input.files && input.files[0] ) {
        var FR = new FileReader();
        FR.onload = function(event) {window.img = event.target.result;};
        FR.readAsDataURL(input.files[0]);
    }
}

var img = 0;
$("#uploader").change(function(){readImage(this);});