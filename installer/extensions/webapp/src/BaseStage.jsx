import Guacamole from 'guacamole-common-js'
import React from 'react'
import './BaseStage.css'
import Card from 'react-bootstrap/Card'
import Table from 'react-bootstrap/Table'
import {Mic, MicMute, ChevronUp, ChevronDown} from 'react-bootstrap-icons'
import RDPClient from './clients/RDPClient'
import PrintClient from './clients/PrintClient2'
import AudioClient from './clients/AudioClient2'
import config from './config'

class BaseStage extends React.Component {

    constructor(props){
        super(props);
        this.myRef = React.createRef();
        this.token = this.props.connection.token;

        this.state = {
            isLoading: true,
            error: false,
            taskbarCollapsed: false,
            printerStatus: '',
            printerName: '',
            audioStatus: ''
        }
        this.audioStreamRDP = null;
        this.recorder = null;
    }

    updatePrinterStatus = (status) => {
        this.setState({ printerStatus: status });
    };

    updatePrinterName = (name) => {
        this.setState({printerName: name});
    };

    updateAudioStatus = (status) => {
        this.setState({ audioStatus: status });
    };

    componentDidMount(){
        const tunnel = new Guacamole.WebSocketTunnel('ws://localhost:8080/');
        const client = new Guacamole.Client(tunnel);
        this.myRef.current.appendChild(client.getDisplay().getElement());

        // Mouse Events
        const mouse = new Guacamole.Mouse(client.getDisplay().getElement());
        mouse.onEach(['mousedown', 'mouseup', 'mousemove'], function sendMouseEvent(e) {
            client.sendMouseState(e.state);
        });

        // Keyboard Events
        const keyboard = new Guacamole.Keyboard(document);
        keyboard.onkeydown = function (keysym) {
            client.sendKeyEvent(1, keysym);
        };
        keyboard.onkeyup = function (keysym) {
            client.sendKeyEvent(0, keysym);
        };

        // Error handling
        tunnel.onerror = (error) => {
            this.setState({isLoading: false, error: true})
        }

        client.onerror = (error) => {
            this.setState({isLoading: false, error: true})
        }

        // to delete 
        this.audioClient = new AudioClient(config, '123', '192.168.178.28')
        this.audioClient.connect();
        this.audioClient.onStatusChange = (state) => {
            this.updateAudioStatus(state)
        }

        this.printClient = new PrintClient(config, '123', 'tom_printer')
        this.printClient.connect();
        this.printClient.onPathReceived = (path) => {
            this.updatePrinterName(path)
        }
        this.printClient.onStatusChange = (state) => {
            this.updatePrinterStatus(state)
        }
        // until here

        // On connect
        client.onstatechange = (state) => {
            if(state === 3){
                this.setState({isLoading: false, error: false})
                if(this.props.connection.type === 'RDP'){
                    this.rdpManager = new RDPClient(client);
                    this.updateAudioStatus('Audio is managed by RDP')
                    this.updatePrinterStatus('Using RDP printing')
                    this.updatePrinterName('Guacamole Printer')
                }
                else{
                    /*
                    this.vncPrinter = new PrintClient('192.168.178.29', 8010, 'tom_printer')
                    this.vncPrinter.connect();
            
                    this.vncPrinter.onStatusChange = (state) => {
                        this.updatePrinterStatus(state)
                    }

                    this.vncPrinter.onPathReceived = (path) => {
                        this.updatePrinterName(path)
                    }
                    
            
                    this.audioClient = new AudioClient('192.168.178.28', 'ws://localhost:8020/');
                    this.audioClient.connect();
                    this.audioClient.onStatusChange = (state) => {
                        this.updateAudioStatus(state)
                    }
                    */
                }
            }
        }

        client.connect('token='+this.token); 

        this.client = client;
    }


    componentWillUnmount(){
        this.client.disconnect();
        if(this.audioClient)
            this.audioClient.disconnect();
        if(this.vncPrinter)
            this.vncPrinter.disconnect();
    }

    toggleAudio = (event) => {
        this.setState((prevState) => {
            const newState = !prevState.audioEnabled;
            if(newState)
                this.audioClient.startRecording();
            else
                this.audioClient.stopRecording();
            return {audioEnabled: newState}
        });
    }

    toggleTaskbar = () => {
        this.setState((prevState) => ({
            taskbarCollapsed: !prevState.taskbarCollapsed
        }));
    }

    
    render(){
        return(
            <div>
                <button onClick={this.toggleTaskbar} className="btn btn-primary mb-1">
                    {this.state.taskbarCollapsed ? 'Show taskbar' : 'Hide taskbar'} {this.state.taskbarCollapsed ? <ChevronDown /> : <ChevronUp />}
                </button>
                {!this.state.taskbarCollapsed && (
                <Card className='taskbar'>
                    <div className='d-flex justify-content-around align-items-start m-2'>
                        <div>
                            <span className='heading'>Connection Info:</span>
                            <Table striped bordered hover size='sm'>
                                <thead>
                                    <tr>
                                        <th>Parameter</th>
                                        <th>Value</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>Connection Type</td>
                                        <td>{this.props.connection.type}</td>
                                    </tr>
                                    <tr>
                                        <td>Machine Address</td>
                                        <td>{this.props.connection.address}</td>
                                    </tr>
                                    <tr>
                                        <td>Operating System</td>
                                        <td>{this.props.connection.os}</td>
                                    </tr>
                                </tbody>
                            </Table>
                        </div>
                        <div>
                            <span className='heading'>Audio:</span>
                            <button disabled={this.props.connection.type==='RDP' || this.state.audioStatus != 'ready'} style={{marginBottom: '10px'}} className={this.state.audioEnabled ? 'btn btn-success' : 'btn btn-danger'} onClick={this.toggleAudio}>
                                {this.state.audioEnabled ? <Mic /> : <MicMute />}
                            </button>
                            <br/>
                            <span>Status: {this.state.audioStatus}</span>
                        </div>
                        <div>
                            <span className='heading'>Printer:</span>
                            <span>Status: {this.state.printerStatus}</span>
                            <br/>
                            <span>Printer path: {this.state.printerName}</span>
                        </div>
                    </div>       
                </Card>
                )}
                <div ref={this.myRef} />
                {this.state.isLoading && (
                    <div className='loading-overlay'>
                        <span>Loading ...</span>
                    </div>
                )}
                {this.state.error && (
                    <div className='error-overlay'>
                    <span>An error occured</span>
                </div>
                )}
            </div>      
        );
    }

}
export default BaseStage;