'use strict'


var myApp = angular.module('myApp', ['ngRoute','myApp.makePool','myApp.joinPool','myApp.joinTeam','myApp.login','myApp.viewPool','myApp.makeTeam','myApp.register','myApp.approveTeamJoin','myApp.logout','myApp.nav','myApp.triggers','myApp.confirmEmail','myApp.forgotPassword','myApp.forgotPasswordChange','myApp.confirmTeamEmail','myApp.adminApproveTeam','myApp.footer'])



.directive('convertToNumber', function() {
  return {
    require: 'ngModel',
    link: function(scope, element, attrs, ngModel) {
      ngModel.$parsers.push(function(val) {
        return parseInt(val, 10);
      });
      ngModel.$formatters.push(function(val) {
        return '' + val;
      });
    }
  };
})
.config(function ($routeProvider,$httpProvider) {
  $httpProvider.defaults.withCredentials = true;
  $routeProvider
    // .when('/', {
    //   access: {restricted: false},
    //   controller: 'navController',
    //   templateUrl: 'static/partials/home.html'
    // })
    .otherwise({
      redirectTo: '/'
    });
});
// https://github.com/adamalbrecht/ngModal
myApp.provider("ngModalDefaults", function() {
  return {
    options: {
      closeButtonHtml: "<span class='ng-modal-close-x'>X</span>"
    },
    $get: function() {
      return this.options;
    },
    set: function(keyOrHash, value) {
      var k, v, _results;
      if (typeof keyOrHash === 'object') {
        _results = [];
        for (k in keyOrHash) {
          v = keyOrHash[k];
          _results.push(this.options[k] = v);
        }
        return _results;
      } else {
        return this.options[keyOrHash] = value;
      }
    }
  };
});
myApp.directive('modalDialog', [
  'ngModalDefaults', '$sce', function(ngModalDefaults, $sce) {
    return {
      restrict: 'E',
      scope: {
        show: '=',
        dialogTitle: '@',
        dialogSubtitle: '@',
        dialogSub2title: '@',
        dialogSub3title: '@',
        dialogSub4title: '@',
        onClose: '&?'
      },
      replace: true,
      transclude: true,
      link: function(scope, element, attrs) {
        var setupCloseButton, setupStyle;
        setupCloseButton = function() {
          return scope.closeButtonHtml = $sce.trustAsHtml(ngModalDefaults.closeButtonHtml);
        };
        setupStyle = function() {
          scope.dialogStyle = {};
          if (attrs.width) {
            scope.dialogStyle['width'] = attrs.width;
          }
          if (attrs.height) {
            return scope.dialogStyle['height'] = attrs.height;
          }
        };
        scope.hideModal = function() {
          return scope.show = false;
        };
        scope.$watch('show', function(newVal, oldVal) {
          if (newVal && !oldVal) {
            document.getElementsByTagName("body")[0].style.overflow = "hidden";
          } else {
            document.getElementsByTagName("body")[0].style.overflow = "";
          }
          if ((!newVal && oldVal) && (scope.onClose != null)) {
            return scope.onClose();
          }
        });
        setupCloseButton();
        return setupStyle();
        // ng-bind='dialogSubtitles'
      },
      template: "<div class='ng-modal' ng-show='show'>\n  <div class='ng-modal-overlay' ng-click='hideModal()'></div>\n  <div class='ng-modal-dialog' ng-style='dialogStyle'>\n    <span class='ng-modal-title' ng-show='dialogTitle && dialogTitle.length' ng-bind='dialogTitle'></span>\n  <span class='ng-modal-subtitle' ng-show='dialogSubtitle && dialogSubtitle.length' ng-bind='dialogSubtitle'></span>\n  <span class='ng-modal-subsubtitle' ng-show='dialogSub2title && dialogSub2title.length' ng-bind='dialogSub2title'></span>\n <span class='ng-modal-sub3title' ng-show='dialogSub3title && dialogSub3title.length' ng-bind='dialogSub3title'></span>\n <span class='ng-modal-sub3title' ng-show='dialogSub4title && dialogSub4title.length' ng-bind='dialogSub4title'></span> \n<div class='ng-modal-close' ng-click='hideModal()'>\n      <div ng-bind-html='closeButtonHtml'></div>\n    </div>\n    <div class='ng-modal-dialog-content' ng-transclude></div>\n  </div>\n</div>"
    };
  }
]);


myApp.filter('relativedate', ['$filter', function ($filter) {
  return function (rel, format) {
    let date = new Date();
    date.setDate(date.getDate() + rel);
    return $filter('date')(date, format || 'MM-dd-yyyy')
  };
}]);

myApp.filter('relativedateISO', ['$filter', function ($filter) {
  return function (rel, format) {
    let date = new Date();
    date.setDate(date.getDate() + rel);
    return $filter('date')(date, format || 'yyyy-MM-dd')
  };
}]);

myApp.filter('yesNo', function() {
    return function(input) {
        return input ? 'yes' : 'no';
    }
});
// usage: {{array | joinBy : ', '}}
myApp.filter('joinBy', function () {
        return function (input,delimiter) {
            return (input || []).join(delimiter || ',');
        };
    });


myApp.filter('relativeFromTime', ['$filter', function ($filter) {
  return function (rel,time, format) {
    var copy = new Date(time.getTime());
    copy.setHours(copy.getHours() + rel);
    return $filter('date')(copy, format || 'hh:mma')
  };
}]);


myApp.filter('relativeFromMins', ['$filter', function ($filter) {
  return function (rel,time, format) {
    if (typeof time.getTime === 'function'){
      var copy = new Date(time.getTime());
    }
    else{
      var copy = new Date(Date.parse(time));
    }
    copy.setMinutes(copy.getMinutes() + rel);
    return $filter('date')(copy, format || 'hh:mma')
  };
}]);

myApp.filter('relativeFromDate', ['$filter', function ($filter) {
  return function (rel,date,time, format) {
    var copy = new Date(date.getTime());
    copy.setHours(time.getHours() + rel);
    copy.setMinutes(time.getMinutes());
    return $filter('date')(copy, format || 'mediumDate')
  };
}]);


myApp.run(function ($rootScope, $location, $route, AuthService,$log) {
  $rootScope.$on('$routeChangeStart',
    function (event, next, current) {

      AuthService.getUserStatus()
      .then(function(){
        var logged_in = AuthService.isLoggedIn();
        $rootScope.logged_in = logged_in;

        if (logged_in){
          AuthService.requestMyEmail()
          .then(function(){
            $rootScope.myEmail=AuthService.getMyEmail();
          });
        }

        if (!logged_in && next && next.access.restricted){
          $location.path('/login');
          $route.reload();
        }
      });


    });
});
