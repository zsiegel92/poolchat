'use strict'

angular.module('myApp.triggers', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider
    .when('/triggers', {
      templateUrl: 'static/triggers/triggers.html',
      controller: 'triggerController',
      access: {restricted: true}
    });
}])
.controller('triggerController',
  ['$scope', '$location', 'AuthService',
  function ($scope, $location, AuthService) {
    $scope.resultText=undefined;

    $scope.getResult = function () {
    };
    $scope.clearScope = function() {
    };
    $scope.dropTabs = function() {
    };
    $scope.getPoolInfo = function() {
    };
    $scope.doGroupThere = function() {
    };
    $scope.repeatGroupThere = function() {
    };
    $scope.sendSomeEmails = function() {
    };
    $scope.sendAllEmails = function() {
    };
    $scope.clearScope = function() {
    };

}]);
