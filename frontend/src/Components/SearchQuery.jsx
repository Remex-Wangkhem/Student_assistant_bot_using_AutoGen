import { useState } from 'react';
import { Box, Input, Button, Flex } from '@chakra-ui/react';
import { IoSend } from "react-icons/io5";

const SearchQuery = ({ onSend }) => {
    const [userInput, setUserInput] = useState('');

    const handleSend = () => {
        if (userInput.trim() !== '') {
            onSend(userInput);
            console.log('Working')
            setUserInput('');
        }
    };

    return (
        <Box
            p="4"
            bg="gray.100"
            borderTopWidth="1px"
            width="59rem"
            position="fixed"
            bottom="0"
            left="0"
        >
            <Flex>
            <Input
                    id="chat-input"
                    name="chat-input"
                    flex="1"
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Type your message..."
                />
                <Button colorScheme="teal" onClick={handleSend}>
                    <IoSend/>
                    {/* {isLoading ? <BeatLoader size={8} color="white" /> : 'Send'} */}
                </Button>
            </Flex>
        </Box>
    );
};

export default SearchQuery;
