
var name_js_from = '';
var room_js_from = '';

sub_form = $('#submit')
sub_form.on('click', function(e){
	e.preventDefault();
	console.log(e);
	// name_js_from = $('#name').val();
	// room_js_from = $('#room').val();
	// $.post('/html', $(this).serialize(), function(e)($('body').html(e)));

	host = window.location.hostname;
	if (host == 'localhost')
		{host+=':4042/';}
	else
		{host = 'ngrok.com:49689/';}

	ws = new WebSocket('ws://'+host);
	ws.onopen = function() {
		console.log("Connection opened...");
		data = {
				'name'       : $('#name').val(),
				'token'      : $('#room').val(),
				'room'       : room-js_from,
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
		console.log('ANS',event);
		if data_json['body']{
			$('body').html(data_json['body'])
		}
		if (data_json['message'] || data_json['image']){
			var mes = "<p class='message'><span class = 'message'>";
			if (data_json['message']){mes += data_json['message'];}
			mes += '</span>';
			if (data_json['image']){mes+='<a class = "message" href="'+data_json['image']+'" data-lightbox="example-2"><img src="'+data_json['image']+'" class = "message"></a>';}
			mes += "</p>";
			$('#message').append(mes);
		}
		if (data_json['user_list']){
			$('#user_list').html('');
			$.each(data_json['user_list'],function(key,val){
				if (val == '{{name}}'){$('#user_list').append('<p class = "user_list_item self">'+key+':'+val+'</p>');}
				else{$('#user_list').append('<p class = "user_lit_itme">'+key+':'+val+'</p>');}
				});
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
})




// ws = new WebSocket('ws://'+host);
// ws.onopen = function() {
// 	console.log("Connection opened...");
// 	data = {
// 			'name'       : name_js_from,
// 			'token'      : token_js_from,
// 			'room'       : room-js_from,
// 			'room_token' : room_token_js_from,
// 			'type_msg'   : 'login'
// 		};
// 	console.log(data);
// 	ws.send(JSON.stringify(data));
//     };
// ws.onclose   = function() { console.log("Connection closed...");};
// ws.error     = function(event) { console.log("Connection error..."+event);};
// ws.onmessage = function(event) {
// 	data_json = $.parseJSON(event['data']);
// 	console.log('ANS',event);
// 	if (data_json['message'] || data_json['image']){
// 		var mes = "<p class='message'><span class = 'message'>";
// 		if (data_json['message']){mes += data_json['message'];}
// 		mes += '</span>';
// 		if (data_json['image']){mes+='<a class = "message" href="'+data_json['image']+'" data-lightbox="example-2"><img src="'+data_json['image']+'" class = "message"></a>';}
// 		mes += "</p>";
// 		$('#message').append(mes);
// 	}
// 	if (data_json['user_list']){
// 		$('#user_list').html('');
// 		$.each(data_json['user_list'],function(key,val){
// 			if (val == '{{name}}'){$('#user_list').append('<p class = "user_list_item self">'+key+':'+val+'</p>');}
// 			else{$('#user_list').append('<p class = "user_lit_itme">'+key+':'+val+'</p>');}
// 			});
// 		}
// 	};




function readImage(input) {
    if ( input.files && input.files[0] ) {
        var FR = new FileReader();
        FR.onload = function(event) {window.img = event.target.result;};
        FR.readAsDataURL(input.files[0]);
        // return img
    }
}

var img = 0;
$("#uploader").change(function(){readImage(this);});
