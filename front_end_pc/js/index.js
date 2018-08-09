var vm = new Vue({
    el: '#app',
    // 声明Vue使用的模板变量语法
    delimiters: ['[[', ']]'],
    data: {
        host,
        username: sessionStorage.username || localStorage.username,
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
        cart_total_count: 0, // 购物车总数量
        cart: [], // 购物车数据,
        f1_tab: 1, // 1F 标签页控制
        f2_tab: 1, // 2F 标签页控制
        f3_tab: 1, // 3F 标签页控制
    },
    mounted: function(){
        this.get_cart();
    },
    methods: {
        // 退出
        logout: function(){
            sessionStorage.clear();
            localStorage.clear();
            location.href = '/login.html';
        },
        // 获取购物车数据
        get_cart: function(){

        }
    }
});