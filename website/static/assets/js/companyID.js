function getCompanyID(id) {
    fetch('/profile', {
        method: 'POST',
        body: JSON.stringify({ compID: id})
    })
}