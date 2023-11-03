// Initialize Firebase
import {app, database} from './viewCounter'


function count_view(viewers_ip) {
  var views; 

  var ip_to_string = viewers_ip.toString();

  // ip_to_string = replaceAll(".", "-")
  for (var i, i = 0; i < ip_to_string.length; i++) {
    ip_to_string = ip_to_string.replace(".", "-")
  }

  database.ref.child("page_views/" + ip_to_string).set({
    viewers_ip: viewers_ip
  })

  database.ref.child("page_views/").on("value", function(snapshot) {
    views = snapshot.numChildren();
    document.getElementById("view_count").innerHTML = views + "here";
  });
}
