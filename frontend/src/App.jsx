import React, { useState } from 'react';
import { Box, Flex } from '@chakra-ui/react';
import SideBar from './Components/SideBar.jsx';
import Chat from './Components/NewChat.jsx';
import Agents from './Components/Agents.jsx';
import SearchQuery from './Components/SearchQuery.jsx';
import Header from './Components/Header.jsx';
import Completion from './Components/Completion.jsx';
import axios from 'axios';

const App = () => {
  const [messages, setMessages] = useState([]);

  const handleSendMessage = async (message) => {
    setMessages(prevMessages => [...prevMessages, { text: message, type: 'user' }]);


    // Fetching From Backend
    try {
        const response = await axios.post('http://127.0.0.1:5000/chat', {
            message: message,
        });

        const agentReply = response.data.reply;
        const sources = response.data.sources;

        if (typeof agentReply !== 'string') {
            throw new Error("Agent reply is not a string.");
        }

        setMessages(prevMessages => [
            ...prevMessages,
            { text: agentReply, type: 'agent',sources }
        ]);

    } catch (error) {
        console.error("Error sending message:", error);
        setMessages(prevMessages => [
            ...prevMessages,
            { text: 'Sorry, something went wrong. Please try again.', type: 'agent' }
        ]);
    }
};
  // Handler function to handle agent button clicks
  const handleAgentSelect = (message) => {
    setMessages(prevMessages => [...prevMessages, { text: message, type: 'user' }]);
    setTimeout(() => {
      setMessages(prevMessages => [
        ...prevMessages,
        { text: 'This is an automated response.', type: 'agent' }
      ]);
    }, 500);
  };

  return (
    <Flex direction="column" h="100vh">
      <div className="fixed  top-0 left-0 w-full">
      <Header />
      </div>
      <Flex flex="1" marginTop="4rem">
        <SideBar />
        <Agents onSelectAgent={handleAgentSelect} />
        <Completion/>
        <Chat messages={messages} />
      </Flex>
      <SearchQuery onSend={handleSendMessage} />
    </Flex>
  );
};

export default App;