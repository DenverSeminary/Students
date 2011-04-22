$(document).ready(	
	function () {
		cx_id = $("#cx_id").val();
		/*	STILL NEED TO IMPLEMENT THESE HIDDEN ELEMENTS BELOW
		 * firstname = $("#firstname").val();
		lastname = $("#lastname").val();
		email = $("#email").val();
		*/
		$("#emails").fadeIn("fast");		
		$("#v_email").click(
			function () {
				$("#emails").fadeOut("fast",
					function () {						
						value = $('input:radio[name=email]:checked').val();						
						value = value.replace(/^\s*|\s*$/g,'');
						alert(value);	
						alert("'valtype=email2" + "&value=" + value + "&cx_id="+ cx_id + "'");
						$.ajax(
							{
								type: "POST", 
								url: "/reg_validate", 
								data: "valtype=email2" + "&value=" + value + "&cx_id="+ cx_id,
								success:
									function (data) {
										if (data=="1"){											
											$("#addrs").fadeIn("fast");
										}
										else {
											$("#main").html(data);
										}
									}
							}
						);																	
					}
				);				
			}
		);
		$("#v_addr").click(
			function () {
				$("#addrs").fadeOut("fast",
					function () {						
						value = $('input:radio[name=addr]:checked').val();						
						value = value.replace(/^\s*|\s*$/g,'');
						alert(value);	
						alert("'valtype=addr_line1" + "&value=" + value + "&cx_id="+ cx_id + "'");
						$.ajax(
							{
								type: "POST", 
								url: "/reg_validate", 
								data: "valtype=addr_line1" + "&value=" + value + "&cx_id="+ cx_id,
								success:
									function (data) {
										if (data=="1"){											
											$("#zips").fadeIn("fast");
										}
										else {
											$("#main").html(data);
										}
									}
							}
						);																	
					}
				);				
			}
		);
		$("#v_zip").click(
			function () {
				$("#zips").fadeOut("fast",
					function () {						
						value = $('input:radio[name=zip]:checked').val();						
						value = value.replace(/^\s*|\s*$/g,'');
						alert(value);	
						alert("'valtype=zip" + "&value=" + value + "&cx_id="+ cx_id + "'");
						$.ajax(
							{
								type: "POST", 
								url: "/reg_validate", 
								data: "valtype=zip" + "&value=" + value + "&cx_id="+ cx_id,
								success:
									function (data) {
										if (data=="1"){											
											$("#majors").fadeIn("fast");
										}
										else {
											$("#main").html(data);
										}
									}
							}
						);																	
					}
				);				
			}
		);
		$("#v_major").click(
			function () {
				$("#majors").fadeOut("fast",
					function () {						
						value = $('input:radio[name=major]:checked').val();						
						value = value.replace(/^\s*|\s*$/g,'');
						alert(value);	
						alert("'valtype=major" + "&value=" + value + "&cx_id="+ cx_id + "'");
						$.ajax(
							{
								type: "POST", 
								url: "/reg_validate", 
								data: "valtype=major" + "&value=" + value + "&cx_id="+ cx_id,
								success:
									function (data) {
										if (data=="1"){											
											$("#main").html("YOU PASSED!!!!");
										}
										else {
											$("#main").html(data);
										}
									}
							}
						);																	
					}
				);				
			}
		);
	});
