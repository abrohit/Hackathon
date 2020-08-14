function submitResponse(){

    var response = document.getElementById("id1").value;
    var sessionID = document.getElementById("id2").value;
    var username = document.getElementById("id3").value;

    if(response.length == 0 || sessionID.length == 0 || username.length ==0){
      alert('One or many boxes are empty!')
    }else{
      const Url = 'http://classroomplus.herokuapp.com/frq/';
      
    
     }
