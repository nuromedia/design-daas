const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));


class PrintClient{

    constructor(baseUrl){
        this.subscribed = false;
        this.baseUrl = baseUrl
    }

    // Provide the address of the API which will receive notifications for created files
    async subscribe(url){
        const response = await fetch(this.baseUrl + '/api/subscribe', {
            method: 'post',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'url': url})
        });
        const data = await response.json();
        return response;
    }
    
    // Check if a printer for a given ID exists
    async checkForPrinter(id) {
        const response = await fetch(this.baseUrl + '/api/check_for_printer', {
            method: 'post',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'id': id})
        });
        const data = await response.json();

        return data['exists'];
    }

    // Create a printer for a given ID
    async createPrinter(id){
        const response = await fetch(this.baseUrl + '/api/create_printer', {
            method: 'post',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'id': id})
        });
        const data = await response.json();

        return response;
    }

    // Delete a printer for given ID
    async deletePrinter(id){
        const response = await fetch(this.baseUrl + '/api/delete_printer', {
            method: 'post',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'id': id})
        });
        const data = await response.json();
        
        return response;
    }

}

module.exports = PrintClient;