$(document).ready(	
	function () {
		cx_id = $("#cx_id").val();		
		firstname = $("#firstname").val();
		lastname = $("#lastname").val();
		email = $("#email").val();		
		$("#retry").click(
			function ()
			{
				alert($("#retry.frm").html());
				$("#retry_frm").submit();
			}
		);
		$("#emails").fadeIn("fast");		
		$("#v_email").click(
			function () {
				$("#emails").fadeOut("fast",
					function () {						
						value = $('input:radio[name=vemail]:checked').val();						
						value = value.replace(/^\s*|\s*$/g,'');						
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
						$.ajax(
							{
								type: "POST", 
								url: "/reg_validate", 
								data: "valtype=major" + "&value=" + value + "&cx_id="+ cx_id,
								success:
									function (data) {
										if (data=="1"){											
											$("#main").html("YOU PASSED!!!!");
											// here we need to, instead of respond with "YOU PASSED", register the user and then redirect to /
											alert(email + firstname + lastname + cx_id);	
											
											$.ajax (
												{
													type: "POST", 
													url: "/finish",
													data: "cx_id=" + cx_id + "&firstname=" + firstname + "&lastname=" + lastname + "&email=" + email,
													success:
														function (data) {
															alert(data);
														}
												}
											)
																					
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
