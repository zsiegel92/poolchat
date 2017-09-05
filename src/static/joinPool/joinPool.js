'use strict'

angular.module('myApp.joinPool', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider
    .when('/joinPool/:id/name/:name/address/:address/date/:date/time/:time/dateTime/:dateTime/email/:email/notice/:notice/latenessWindow/:latenessWindow/carpooler/cpname/:cpname/cpfirst/:cpfirst/cplast/:cplast/cpemail/:cpemail/past_addresses/:past_addresses/max_seats/:max_seats/ever_must_drive/:ever_must_drive/ever_organizer/:ever_organizer/:resubmit/:repAddress?/:repNumSeats?/:repPreWindow?/:repOnTime?/:repMustDrive?', {
      templateUrl: 'static/joinPool/joinPool.html',
      controller: 'joinPoolController',
      access: {restricted: true}
    });
}])

.controller('joinPoolController',['$scope', '$location', 'AuthService','$route', '$routeParams','$log','$http','$filter','$window','$q',
  function ($scope, $location, AuthService,$route,$routeParams,$log,$http,$filter,$window,$q){

    var f = $window.decodeURIComponent;
    var r = $routeParams;
    $scope.address_confirmed=false;
    $scope.disabled=false;
    $scope.using_preset=false;
    // $scope.tripForm.ngOn_time = false;
    // $scope.tripForm.ngMust_drive = false;
    $scope.tripForm={};

    $scope.pool = {'id':f(r.id),'name':f(r.name),'address':f(r.address),'date':f(r.date),'time':f(r.time),'dateTime':f(r.dateTime),'email':f(r.email),'notice':f(r.notice),'latenessWindow':f(r.latenessWindow)};
    $scope.carpooler = {'name':f(r.cpname),'first':f(r.cpfirst),'last':f(r.cplast),'email':f(r.cpemail)};
    $scope.past_addresses=JSON.parse(f(r.past_addresses));
    $scope.max_seats = f(r.max_seats);
    $scope.ever_must_drive = f(r.ever_must_drive);
    $scope.ever_organizer = f(r.ever_organizer);

    $scope.pool_dateTime = new Date(Date.parse($scope.pool.dateTime));

    $scope.setDefaults = function(){
      $scope.tripForm.ngOn_time = ($scope.ever_organizer==1);
      $scope.tripForm.ngMust_drive = ($scope.ever_must_drive==1);
    };
    $scope.setDefaults();


    // $scope.zoneOffset = $scope.pool.dateTime.getTimezoneOffset();
    // var pool_dateTime = new Date(Date.parse($scope.pool.dateTime));
    // $scope.zoneOffset = pool_dateTime.getTimezoneOffset();
    $scope.unconfirm = function(){
      $log.log("unconfirm-ing");
      $scope.address_confirmed=false;
      $scope.set_all_prefill_false();
    };
    $scope.un_preset = function(){
      $log.log("un preset-ing");
      $scope.address_confirmed=false;
      $scope.using_preset = false;
      $scope.set_all_prefill_false();
    };
    // $scope.prefill_disabled = Array.from({length:$scope.past_addresses.length}, i => false); //ES6 only!
    $scope.prefill_disabled =Array($scope.past_addresses.length).fill(false);//ES6 only!
    $scope.use_preset = function(address,index){
      $scope.using_preset=true;
      $scope.tripForm.ngAddress=address;
      $scope.address_confirmed=true;
      $scope.set_all_prefill_false();
      $scope.prefill_disabled[index]=true;
    };

    $scope.set_all_prefill_false = function() {
      for (var i = 0; i < $scope.prefill_disabled.length; i++){
        $scope.prefill_disabled[i]=false;
      }
    };


    $scope.preTime = function(baseTimeString,preWindow){
      let dt = new Date(Date.parse(baseTimeString));
      let relDt = new Date(dt.getTime() - preWindow*60*1000);
      return relDt;
    };
    $scope.preTimes = [15,20,25,30,35,40,45,50,55,60];

    $scope.backto_view = function(){
      $location.path('/viewPool');
    };

    // Returns: {'formatted_address':fa,'image_url':iu}
    var conf_address = function(address){
      $scope.disabled = true;

      return $http.post('/api/confirm_address/',
            $.param(
              {
                address:address
              }
            ),
            {headers: {'Content-Type': 'application/x-www-form-urlencoded'}})
        .then(function(response) {
          $scope.disabled = false;

          $log.log({'image_url':response.data.image_url,'formatted_address':response.data.formatted_address});

            return {'image_url':response.data.image_url,'formatted_address':response.data.formatted_address};
            // return response.data;

        }).
        catch(function(response) {
          $scope.disabled = false;
          $log.log(response.data);
          return "error";
        });
    };
    conf_address($scope.pool.address).then((response)=>{
     $scope.pool_info = response;
   });

   $scope.confirmAddress = function(){
    if ($scope.tripForm.ngAddress && $scope.tripForm.ngAddress !=''){
          conf_address($scope.tripForm.ngAddress).then((response)=>{
          $scope.address_confirmed=true;
          $scope.tripForm.ngAddress=response.formatted_address;
          $scope.trip_image_url=response.image_url;
    });
    }

   };



  $scope.joinTrip = function() {

    $scope.disabled = true;

    $log.log("Registering:");
    $log.log(                {
                  address:$scope.tripForm.ngAddress,
                  num_seats:$scope.tripForm.ngNumSeats,
                  preWindow:$scope.tripForm.ngPreWindow,
                  on_time:$scope.tripForm.ngOn_time,
                  must_drive:$scope.tripForm.ngMust_drive,
                  pool_id:$scope.pool.id,
                  resubmit:$scope.resubmit
                });
    $http.post('/api/create_trip/',
              $.param(
                {
                  address:$scope.tripForm.ngAddress,
                  num_seats:$scope.tripForm.ngNumSeats,
                  preWindow:$scope.tripForm.ngPreWindow,
                  on_time:$scope.tripForm.ngOn_time,
                  must_drive:$scope.tripForm.ngMust_drive,
                  pool_id:$scope.pool.id,
                  resubmit:$scope.resubmit
                }
              ),
              {headers: {'Content-Type': 'application/x-www-form-urlencoded'}})

      .then(function(response) {
        var baseURL = $location.$$absUrl.replace($location.$$url, '');
        $scope.disabled = false;
        $log.log("Registration response:");
        $log.log(response.data);
        $scope.resultText=response.data;
        alert("Make sure you're ready to go before this event on " + $scope.pool.date + " at " + $scope.pool.time + "! Visit " + baseURL + "/viewPool to see the events you're part of!");
        $location.path('/viewPool');

      }).
      catch(function(response) {
        $scope.disabled = false;
        if (response.status==409){
          $scope.resultText="Redundant entry!";
          $log.log(response.data);
        }
        else{
          $log.log(response.data);
          $scope.errorMessage = response.data;
          $scope.resultText="Error registering Trip.";
        }
      });
  };


  $scope.prefill_fromPath = function(){
    $scope.resubmit = (f(r.resubmit) == 'true');
    if ($scope.resubmit == true){
      $log.log("Resubmission in progress!");
      $log.log("address: " + f(r.repAddress) + ", num_seats: " + Number(f(r.repNumSeats)) + ', preWindow: ' + Number(f(r.repPreWindow)) + ', on_time: ' + Boolean(Number(f(r.repOnTime))) + ', must_drive: ' + Boolean(Number(f(r.repMustDrive))) );

      // Somehow, these weren't setting directly, so I set in ng-init
      $scope.oldAddress=f(r.repAddress);
      $scope.oldPreWindow = f(r.repPreWindow);
      $scope.oldNumSeats = f(r.repNumSeats);

      $scope.tripForm.ngOn_time= Boolean(Number(f(r.repOnTime)));
      $scope.tripForm.ngMust_drive = Boolean(Number(f(r.repMustDrive)));
      $scope.address_confirmed=true;
    }
  };


  $scope.prefill_fromPath();
}]);


