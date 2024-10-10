import { Flex, Box, Text, VStack } from '@chakra-ui/react';

const Completion = () => {
    const completionBoxes = [
        { title: 'Completion List', content: null },
        { title: 'Completed Task 1', content: null },
        { title: 'Completed Task 2', content: null },
    ];

    return (
        <Flex flexDirection="column" marginLeft={2} height="full">
            {completionBoxes.map((box, index) => (
                <Box
                    key={index}
                    w="20rem"
                    p="4"
                    bg="gray.200"
                    borderLeftWidth="1px"
                    h="13rem"
                    marginTop={index > 0 ? 2 : 0} 
                >
                    <VStack spacing="4" align="stretch">
                        <Text fontSize="lg" fontWeight="bold">{box.title}</Text>
                    </VStack>
                </Box>
            ))}
        </Flex>
    );
};

export default Completion;
