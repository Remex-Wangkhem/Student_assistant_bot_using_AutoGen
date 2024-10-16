import React, { useState } from 'react';
import { Box, Flex } from '@chakra-ui/react';
import SideBar from './Components/SideBar.jsx';
import Chat from './Components/Chat.jsx';
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
      const response = await fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userInput }),
      });

      const data = await response.json();

      if (data.error) {
        setMessages(prevMessages => [
          ...prevMessages,
          { type: 'error', text: data.error }
        ]);
      } else {
        // the agent response to the chat
        setMessages(prevMessages => [
          ...prevMessages,
          { type: 'agent', text: data.message }
        ]);

        // Optionally handle courses and faculty lists
        if (data.faculty.length > 0) {
          // Convert faculty list to table format
          const facultyTable = (
            <table>
              <thead>
                <tr>
                  <th>Faculty Name</th>

                  <th>Gender</th>
                  &nbsp;
                  &nbsp;
                  <th>Department</th>
                </tr>
              </thead>
              <tbody>
                {data.faculty.map((faculty, index) => (
                  <tr key={index}>
                    <td>{faculty.name}</td>
                    <td>{faculty.gender === 'Male' ? 'Male' : 'Female'}</td>
                    &nbsp;
                    &nbsp;
                    &nbsp;
                    <td>{faculty.department}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          );

          // Add the table to the chat
          setMessages(prevMessages => [
            ...prevMessages,
            { type: 'agent', text: facultyTable }
          ]);
        }
      }
    } catch (error) {
      setMessages(prevMessages => [
        ...prevMessages,
        { type: 'error', text: 'Server error. Try again later.' }
      ]);
    // } finally {
    //   // setIsLoading(false);
    //   setUserInput('');
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
        <Completion />
        <Chat messages={messages} />
      </Flex>
      <SearchQuery onSend={handleSendMessage} />
    </Flex>
  );
};

export default App;