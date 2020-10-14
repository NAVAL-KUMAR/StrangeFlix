 alert("hello")
 jQuery(document).ready(function () {
    setInterval(function()
    {
    $.ajax({
      type: "GET",
      url: "/comment_list",
       data: {
            video_id : $('#videoid').val()
      },
      success: function (response) {
        console.log(response);
        $('#commment_list').empty();
        for(var key in response.comments){
            var temp = "<tr><td>"+response.comments[key].text+"</td></tr>";

            $('#commment_list').append(temp);
           // console.log($('#comment_list'));
        }
      }
    });
    },1000);
});