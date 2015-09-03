
var name;
var room;
sub_form = $('#submit')
sub_form.on('click', function(e){
	e.preventDefault();

	name = $('#name').val();
	room = $('#room').val().toLowerCase();

	host = location.origin.replace(/^http/, 'ws') + '/ws'
	ws = new WebSocket(host);
	ws.onopen = function() {
		console.log("Connection opened...");
		data = {
				'name': name,
				'room': room,
				'room_pass': $('#password').val(),
				'type_msg': 'login'
			};
		ws.send(JSON.stringify(data));
	    };
	ws.onclose   = function() { console.log("Connection closed...");};
	ws.error     = function(event) { console.log("Connection error..." + event);};
	ws.onmessage = function(event) {
		console.log('mssss', event.data);
		data_json = $.parseJSON(event['data']);
		// console.log(data_json);
		if (data_json.body){
			$('body').html(data_json.body);

			$("#send").on("click", function(e){
				data = {
							'message' :$('#sending_message').val(),
							'type_msg':'message'
						};
				if (img){data.image = img; img = 0;}
				else {data.image = '';}
				ws.send(JSON.stringify(data));
				$('#sending_message').val('');
				$("#uploader").val('');
				e.preventDefault();
			});
		}
		if (data_json.message || data_json.image){
			var mes = $("<p class='message'></p>");
			// mes.text(data_json.name);
			mes.append($("<span class = 'message'></span>"));
			if (data_json.message){mes.children().append(data_json.message);}
			if (data_json.image){mes.children().append('<a class = "message" href="'+data_json.image+'" data-lightbox="example-2"><img src="'+data_json.image+'" class = "message"></a>');}
			mes.addClass(function(){
				if (name.toLowerCase() == data_json.name.toLowerCase()){return "self";}
				else if ("server" == data_json.name.toLowerCase()){return "system";}
				else {return ""};
			});
			$('#message').append(mes);
		}
		var user_list = $('#user_list');
		if (data_json.user_list){
			user_list.html('');
			$.each(data_json.user_list,function(key,val){
				var user_list_item = $('<span class = "user_list_item"></span>');
				user_list_item.text(key + ':' + val);
				user_list_item.addClass(function(){
					return val.toLowerCase() == name.toLowerCase() ? "self" : "";
				});
				user_list.append(user_list_item);
				});
			}
		};
})

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
