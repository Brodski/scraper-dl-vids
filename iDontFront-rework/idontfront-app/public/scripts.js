function isMobile() {
    const userAgent = navigator.userAgent || navigator.vendor || window.opera;
    let isUserMobile1 = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent)
    let isUserMobile2 = typeof window.orientation !== 'undefined';
    let isUserMobile3 = 'ontouchstart' in window;
    let wid = window.innerWidth <= 768
    return isUserMobile1 || isUserMobile2 || isUserMobile3 || wid
}
